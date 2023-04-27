import os
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, update_session_auth_hash, logout as auth_logout
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Avg

from .forms import UpdateProfileForm, ChangePasswordForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
# Password Reset Imports
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from main.tokens import update_email_token
from django.contrib.auth.models import User
from django.conf import settings
from main.views import auth_login
from .forms import AddCustomerForm, UpdateCustomerForm, UpdateCustomerPasswordForm, AddCategoryForm, \
    UpdateCategoryForm, AddBrandForm, UpdateBrandForm, AddProductForm, UpdateProductForm, ChangeEmailForm, \
    AddCouponForm, UpdateCouponForm, UpdateOrderStatusForm, UpdatePaymentStatusForm
from main.models import Customer, Category, Brand, Product, Coupon, Feedback, Orders, OrderDetails, Payment, Review, \
    DeliveryAddress
import csv
import xlwt
import json
from django.http import HttpResponse, JsonResponse
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.views.generic import TemplateView
import matplotlib.pyplot as plt
import numpy as np
from datetime import date, timedelta
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


# Create your views here.
def is_admin(user):
    return user.is_authenticated and user.is_superuser and user.is_staff and user.is_active


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def dashboard(request):
    # get all recent customers last login
    users = User.objects.filter(is_superuser=False, is_staff=False, is_active=True).order_by('-last_login')[:8]

    customers = Customer.objects.all()

    # get all recent orders
    orders = Orders.objects.all().order_by('-order_date')[:10]

    payments = Payment.objects.all()
    # get all recent sales
    sales = 0
    for order in orders:
        sales += order.total_amount
    # get revenue = sold * (price original - price sale - discount)

    profit = 0
    for order in orders:
        profit += order.profit_order

    # quality product sale
    quality_product_sale = 0
    for order in orders:
        for order_detail in order.orderdetails_set.all():
            quality_product_sale += order_detail.quantity
    # get all product sold count
    product_sold_count = 0
    for product in Product.objects.all():
        product_sold_count += product.sold

    number_customer = User.objects.filter(is_superuser=False, is_staff=False, is_active=True).count()

    # get all view_count of product
    view_count = 0
    for product in Product.objects.all():
        view_count += product.view_count

    # total customers
    total_customers = User.objects.filter(is_superuser=False, is_staff=False, is_active=True).count()
    # total orders
    total_orders = Orders.objects.all().count()
    # total products
    total_products = Product.objects.all().count()
    # total discounts used by customers
    total_discounts = 0
    for order in Orders.objects.all():
        total_discounts += order.total_discount

    # Profit Ratio
    total_profit_ratio = profit / sales * 100
    # Just get one decimal
    total_profit_ratio = round(total_profit_ratio, 1)
    # total feedback
    total_feedback = Feedback.objects.all().count()
    # total review
    total_review = Review.objects.all().count()
    # total payment
    total_payment = Payment.objects.all().count()
    # total review rate
    total_review_rate = Review.objects.all().aggregate(Avg('rate'))
    total_review_rate = total_review_rate['rate__avg']
    # Just get one decimal
    total_review_rate = round(total_review_rate, 1)

    context = {
        'users': users,
        'customers': customers,
        'orders': orders,
        'sales': sales,
        'profit': profit,
        'view_count': view_count,
        'quality_product_sale': quality_product_sale,
        'product_sold_count': product_sold_count,
        'number_customer': number_customer,
        'payments': payments,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_discounts': total_discounts,
        'total_profit_ratio': total_profit_ratio,
        'total_feedback': total_feedback,
        'total_review': total_review,
        'total_payment': total_payment,
        'total_review_rate': total_review_rate,
    }
    return render(request, 'dashboard/base/ad_base.html', context)


# Pagination function
def paginator(request, objects):
    # Set the number of items per page
    per_page = 10

    # Create a Paginator object with the customers queryset and the per_page value
    page = Paginator(objects, per_page)

    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page')

    # Get the current page object from the Paginator object
    page_obj = page.get_page(page_number)
    return page_obj


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def chatbot(request):
    return render(request, 'dashboard/chatbot/chatbot.html')


# Administration Account
# Change email address
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            user = authenticate(username=request.user.username, password=form.cleaned_data['current_password'])
            if user is not None:
                # check if new email is already exist
                new_email = form.cleaned_data['new_email']
                if new_email == request.user.email:
                    form.add_error('new_email', 'New email is same as current email.')
                    return render(request, "dashboard/account/change_email.html", {"form": form})
                elif User.objects.filter(email=new_email).exists():
                    form.add_error('new_email', 'Email is already exist. Please enter another email.')
                    return render(request, "dashboard/account/change_email.html", {"form": form})
                else:
                    user.email = form.cleaned_data['new_email']
                    user.is_active = False
                    user.save()
                    send_verify_new_email(request, user)
                    return render(request, 'dashboard/account/verify_new_email_sent.html', {'email': user.email})
            else:
                form.add_error('current_password', 'Password is incorrect')
                return render(request, "dashboard/account/change_email.html", {"form": form})
    else:
        form = ChangeEmailForm(instance=request.user)
    return render(request, "dashboard/account/change_email.html", {"form": form})


# send email to verify new email
def send_verify_new_email(request, user):
    protocol = 'http' if request.scheme == 'http' else 'https'
    current_site = get_current_site(request)
    mail_subject = 'Update your account.'
    message = render_to_string('dashboard/account/verify_new_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': update_email_token.make_token(user),
        'protocol': protocol,
    })
    to_email = [user.email]
    form_email = 'LCL Shop <lclshop.dev@gmail.com>'
    email = EmailMessage(mail_subject, message, form_email, to_email)
    email.content_subtype = "html"
    email.send()


# activate new email
def activate_new_email_admin(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and update_email_token.check_token(user, token):
        user.is_active = True
        user.save()
        auth_login(request, user)
        messages.success(request, 'Your email has been updated. Now you can login your account.')
        return redirect('/dashboard/change_email/')
    else:
        return render(request, 'dashboard/account/verify_new_email_invalid.html')


# Update profile
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def update_profile(request):
    user = request.user
    # get customer-management object
    customer = Customer.objects.filter(user=user).first()
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES, instance=user,
                                 initial={'address': customer.address, 'mobile': customer.mobile,
                                          'customer_image': customer.customer_image})

        if form.is_valid():
            form.save()
            customer.mobile = form.cleaned_data['mobile']
            customer.address = form.cleaned_data['address']
            if form.cleaned_data['customer_image']:
                customer.customer_image = form.cleaned_data['customer_image']
            customer.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('/dashboard/profile/')
    else:
        form = UpdateProfileForm(instance=user, initial={'address': customer.address,
                                                         'mobile': customer.mobile,
                                                         'customer_image': customer.customer_image})
    return render(request, 'dashboard/account/update_profile.html', {'form': form})


# Change password
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = authenticate(username=request.user.username, password=form.cleaned_data['old_password'])
            if user is not None:
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been updated.')
                return redirect('/dashboard/change_password/')
            else:
                form.add_error('old_password', 'Wrong password. Please try again.')
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, 'dashboard/account/change_password.html', {'form': form})


# Logout
def logout(request):
    auth_logout(request)
    messages.success(request, "You have logged out. See you again. Administrator!")
    return redirect('/auth/login/')


# Customer Management
# Customer table
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def customer_table(request):
    # Get all customers
    users = User.objects.all().order_by('date_joined')
    customers = Customer.objects.all()

    # Get the current page object from the Paginator object
    page_object = paginator(request, users)
    context = {'users': page_object, 'customers': customers}
    return render(request, 'dashboard/manage_customer/customer_table.html', context)


# Add customer
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def add_customer(request):
    if request.method == 'POST':
        form = AddCustomerForm(request.POST, request.FILES)
        if form.is_valid():
            # Create user object
            user = form.save()

            # Create customer object associated with the user
            customer = Customer.objects.create(user=user)
            customer.address = form.cleaned_data['address']
            customer.mobile = form.cleaned_data['mobile']
            customer.customer_image = form.cleaned_data['customer_image']
            customer.save()

            messages.success(request, 'Customer {} added successfully!'.format(customer.user.username))

            if 'save_and_add' in request.POST:
                return redirect('/dashboard/customer/add/')
            elif 'save_and_update' in request.POST:
                return redirect('/dashboard/customer/update/{}/'.format(customer.user.id))
            else:
                return redirect('/dashboard/customer/')
    else:
        form = AddCustomerForm()
    context = {'form': form}
    return render(request, 'dashboard/manage_customer/add_customer.html', context)


# Update customer
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def update_customer(request, user_id):
    user = User.objects.get(id=user_id)
    customer = Customer.objects.get(user_id=user_id)

    if request.method == 'POST':
        form = UpdateCustomerForm(request.POST, request.FILES, instance=user,
                                  initial={'mobile': customer.mobile, 'address': customer.address,
                                           'customer_image': customer.customer_image})
        if form.is_valid():
            # Update customer
            form.save()
            customer = Customer.objects.get(user=user)
            customer.address = form.cleaned_data['address']
            customer.mobile = form.cleaned_data['mobile']
            customer.customer_image = form.cleaned_data['customer_image']
            customer.save()
            messages.success(request, 'Customer {} updated successfully!'.format(user.username))
            # Button actions
            if 'save_and_add' in request.POST:
                return redirect('/dashboard/customer/add/')
            elif 'save_and_update' in request.POST:
                return redirect('/dashboard/customer/update/{}/'.format(customer.user.id))
            else:
                return redirect('/dashboard/customer/')
    else:
        user = User.objects.get(id=user_id)
        form = UpdateCustomerForm(instance=user, initial={'mobile': customer.mobile,
                                                          'address': customer.address,
                                                          'customer_image': customer.customer_image})
    context = {'form': form}
    return render(request, 'dashboard/manage_customer/update_customer.html', context)


# Update password for customer
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def update_customer_password(request, user_id):
    user = User.objects.get(id=user_id)
    customer = Customer.objects.get(user_id=user_id)
    form = UpdateCustomerPasswordForm(request.POST)

    if request.method == 'POST':
        if form.is_valid():
            if user is not None:
                form.save(user)
            # Update customer password
            # Log in the user
            auth_login(request, user)
            messages.success(request, 'Customer {} password updated successfully!'.format(user.username))
            # Button actions
            return redirect('/dashboard/customer/update/' + str(customer.user.id) + '/')
    else:
        user = User.objects.get(id=user_id)
        form = UpdateCustomerPasswordForm()
    context = {'form': form, 'user': user, 'customer': customer}
    return render(request, 'dashboard/manage_customer/update_password_customer.html', context)


# Delete customer
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_customer(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        customer = Customer.objects.get(user=user)
    except ObjectDoesNotExist:
        messages.warning(request, 'The customer {} you are trying to delete does not exist!'.format(user_id))
        return redirect('/dashboard/customer/')

    if user.is_superuser:
        messages.warning(request, 'Admin can not be deleted!')
    else:
        # Delete the customer image file
        if customer.customer_image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(customer.customer_image))
            if os.path.isfile(image_path):
                os.remove(image_path)

        user.delete()
        customer.delete()
        messages.success(request, 'Customer {} deleted successfully!'.format(user.username))
    return redirect('/dashboard/customer/')


# Delete selected customers
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_selected_customer(request, customer_ids):
    if request.method == 'POST':
        # Get a list of user IDs to delete
        user_ids = customer_ids.split("+")
        # Delete the users
        if user_ids:
            for user_id in user_ids:
                try:
                    user = User.objects.get(id=user_id)
                    if user.is_superuser:
                        messages.warning(request, 'Administrator can not be deleted!')
                        return redirect('/dashboard/customer/')
                    else:
                        customer = Customer.objects.get(user=user)
                        # Delete the customer image file
                        if customer.customer_image:
                            image_path = os.path.join(settings.MEDIA_ROOT, str(customer.customer_image))
                            if os.path.isfile(image_path):
                                os.remove(image_path)
                        # Delete the customer
                        customer.delete()
                        user.delete()
                        messages.success(request, 'Customer deleted successfully!')
                except ObjectDoesNotExist:
                    messages.warning(request, f'The customer-management with ID {user_id} does not exist!')
            return redirect('/dashboard/customer/')
        else:
            messages.warning(request, 'Please select at least one customer-management to delete!')
    return redirect('/dashboard/customer/')


# Customer details
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def customer_details(request, user_id):
    user = User.objects.get(id=user_id)
    customer = Customer.objects.get(user_id=user_id)
    context = {'user': user, 'customer': customer}
    return render(request, 'dashboard/manage_customer/customer_details.html', context)


# Search customer
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def search_customer(request):
    search_query = request.POST.get('search', '')
    if request.method == 'POST':
        if search_query == '':
            messages.warning(request, 'Please enter a search term!')
            return redirect('/dashboard/customer/')
        else:
            customers = Customer.objects.filter(user__username__icontains=search_query) | Customer.objects.filter(
                user__email__icontains=search_query) | Customer.objects.filter(
                user__first_name__icontains=search_query) | Customer.objects.filter(
                user__last_name__icontains=search_query) | Customer.objects.filter(
                mobile__icontains=search_query) | Customer.objects.filter(
                address__icontains=search_query)
            users = [customer.user for customer in customers]
            page_object = paginator(request, users)

        if not users:
            messages.success(request, 'No customers found {} !'.format(search_query))
    else:
        users = User.objects.all()
        customers = Customer.objects.all()
        page_object = paginator(request, users)
    context = {'users': page_object,
               'customers': customers,
               'search_query': search_query}
    return render(request, 'dashboard/manage_customer/customer_table.html', context)


# Category Management
# Category table
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def category_table(request):
    # Get all categories
    categories = Category.objects.all().order_by('id')
    page_object = paginator(request, categories)
    context = {'categories': page_object}
    return render(request, 'dashboard/manage_category/category_table.html', context)


# Add category
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def add_category(request):
    if request.method == 'POST':
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, 'Category {} added successfully!'.format(form.cleaned_data['name']))
            if 'save_and_add' in request.POST:
                return redirect('/dashboard/category/add/')
            elif 'save_and_update' in request.POST:
                return redirect('/dashboard/category/update/{}/'.format(category.id))
            else:
                return redirect('/dashboard/category/')
    else:
        form = AddCategoryForm()
    context = {'form': form}
    return render(request, 'dashboard/manage_category/add_category.html', context)


# Update category
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def update_category(request, category_id):
    category = Category.objects.get(id=category_id)
    if request.method == 'POST':
        form = UpdateCategoryForm(request.POST, category=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category {} updated successfully!'.format(form.cleaned_data['name']))
            if 'save_and_add' in request.POST:
                return redirect('/dashboard/category/add/')
            elif 'save_and_update' in request.POST:
                return redirect('/dashboard/category/update/' + str(category_id) + '/')
            else:
                return redirect('/dashboard/category/')
    else:
        category = Category.objects.get(id=category_id)
        form = UpdateCategoryForm(category=category)
    context = {'form': form}
    return render(request, 'dashboard/manage_category/update_category.html', context)


# Delete category
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except ObjectDoesNotExist:
        messages.warning(request, 'The category {} you are trying to delete does not exist!'.format(category_id))
        return redirect('/dashboard/category/')

    category.delete()
    messages.success(request, 'Category {} deleted successfully!'.format(category.name))
    return redirect('/dashboard/category/')


# Delete selected categories
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_selected_category(request, category_ids):
    if request.method == 'POST':
        # Get a list of category IDs to delete
        category_ids = category_ids.split("+")
        # Delete the categories
        if category_ids:
            for category_id in category_ids:
                try:
                    category = Category.objects.get(id=category_id)
                    category.delete()
                    messages.success(request, 'Category deleted successfully!')
                except ObjectDoesNotExist:
                    messages.warning(request, f'The category with ID {category_id} does not exist!')
            return redirect('/dashboard/category/')
        else:
            messages.warning(request, 'Please select at least one category to delete!')
    return redirect('/dashboard/category/')


# Category details
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def category_details(request, category_id):
    category = Category.objects.get(id=category_id)
    context = {'category': category}
    return render(request, 'dashboard/manage_category/category_details.html', context)


# Search category
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def search_category(request):
    search_query = request.POST.get('search', '')
    if request.method == 'POST':
        if search_query == '':
            messages.warning(request, 'Please enter a search term!')
            return redirect('/dashboard/category/')
        else:
            categories = Category.objects.filter(name__icontains=search_query) | Category.objects.filter(
                description__icontains=search_query)
            page_object = paginator(request, categories)

        if not categories:
            messages.success(request, 'No categories found {} !'.format(search_query))
    else:
        categories = Category.objects.all()
        page_object = paginator(request, categories)
    context = {'categories': page_object,
               'search_query': search_query}
    return render(request, 'dashboard/manage_category/category_table.html', context)


# Brand Management
# Brand table
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def brand_table(request):
    # Get all brands
    brands = Brand.objects.all().order_by('id')
    page_object = paginator(request, brands)
    context = {'brands': page_object}
    return render(request, 'dashboard/manage_brand/brand_table.html', context)


# Add brand
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def add_brand(request):
    if request.method == 'POST':
        form = AddBrandForm(request.POST, request.FILES)
        if form.is_valid():
            brand = form.save()
            messages.success(request, 'Brand {} added successfully!'.format(form.cleaned_data['name']))
            if 'save_and_add' in request.POST:
                return redirect('/dashboard/brand/add/')
            elif 'save_and_update' in request.POST:
                return redirect('/dashboard/brand/update/{}/'.format(brand.id))
            else:
                return redirect('/dashboard/brand/')
    else:
        form = AddBrandForm()
    context = {'form': form}
    return render(request, 'dashboard/manage_brand/add_brand.html', context)


# Update brand
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def update_brand(request, brand_id):
    brand = Brand.objects.get(id=brand_id)
    if request.method == 'POST':
        form = UpdateBrandForm(request.POST, request.FILES, brand=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand {} updated successfully!'.format(form.cleaned_data['name']))
            if 'save_and_add' in request.POST:
                return redirect('/dashboard/brand/add/')
            elif 'save_and_update' in request.POST:
                return redirect('/dashboard/brand/update/' + str(brand_id) + '/')
            else:
                return redirect('/dashboard/brand/')
    else:
        brand = Brand.objects.get(id=brand_id)
        form = UpdateBrandForm(brand=brand)
    context = {'form': form}
    return render(request, 'dashboard/manage_brand/update_brand.html', context)


# Delete brand
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_brand(request, brand_id):
    try:
        brand = Brand.objects.get(id=brand_id)
    except ObjectDoesNotExist:
        messages.warning(request, 'The brand {} you are trying to delete does not exist!'.format(brand_id))
        return redirect('/dashboard/brand/')
    brand.delete()
    messages.success(request, 'Brand {} deleted successfully!'.format(brand.name))


# Delete selected brands
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_selected_brand(request, brand_ids):
    if request.method == 'POST':
        # Get a list of brand IDs to delete
        brand_ids = brand_ids.split("+")
        # Delete the brands
        if brand_ids:
            for brand_id in brand_ids:
                try:
                    brand = Brand.objects.get(id=brand_id)
                    brand.delete()
                    messages.success(request, 'Brand deleted successfully!')
                except ObjectDoesNotExist:
                    messages.warning(request, f'The brand with ID {brand_id} does not exist!')
            return redirect('/dashboard/brand/')
        else:
            messages.warning(request, 'Please select at least one brand to delete!')
    return redirect('/dashboard/brand/')


# Brand details
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def brand_details(request, brand_id):
    brand = Brand.objects.get(id=brand_id)
    context = {'brand': brand}
    return render(request, 'dashboard/manage_brand/brand_details.html', context)


# Search brand
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def search_brand(request):
    search_query = request.POST.get('search', '')
    if request.method == 'POST':
        if search_query == '':
            messages.warning(request, 'Please enter a search term!')
            return redirect('/dashboard/brand/')
        else:
            brands = Brand.objects.filter(name__icontains=search_query) | Brand.objects.filter(
                description__icontains=search_query)
            page_object = paginator(request, brands)

        if not brands:
            messages.success(request, 'No brands found {} !'.format(search_query))
    else:
        brands = Brand.objects.all()
        page_object = paginator(request, brands)
    context = {'brands': page_object,
               'search_query': search_query}
    return render(request, 'dashboard/manage_brand/brand_table.html', context)


# Product Management
# Product table
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def product_table(request):
    # Get all products
    products = Product.objects.all().order_by('id')
    page_object = paginator(request, products)
    context = {'products': page_object}
    return render(request, 'dashboard/manage_product/product_table.html', context)


# Add product
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def add_product(request):
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Product {} added successfully!'.format(form.cleaned_data['name']))
            if 'save_and_add' in request.POST:
                return redirect('/dashboard/product/add/')
            elif 'save_and_update' in request.POST:
                return redirect('/dashboard/product/update/{}/'.format(product.id))
            else:
                return redirect('/dashboard/product/')
    else:
        form = AddProductForm()
    context = {'form': form}
    return render(request, 'dashboard/manage_product/add_product.html', context)


# Update product
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def update_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = UpdateProductForm(request.POST, request.FILES, product=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product {} updated successfully!'.format(form.cleaned_data['name']))
            if 'save_and_add' in request.POST:
                return redirect('/dashboard/product/add/')
            elif 'save_and_update' in request.POST:
                return redirect('/dashboard/product/update/' + str(product_id) + '/')
            else:
                return redirect('/dashboard/product/')
    else:
        product = Product.objects.get(id=product_id)
        form = UpdateProductForm(product=product)
    context = {'form': form}
    return render(request, 'dashboard/manage_product/update_product.html', context)


# Delete product
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except ObjectDoesNotExist:
        messages.warning(request, 'The product {} you are trying to delete does not exist!'.format(product_id))
        return redirect('/dashboard/product/')
    product.delete()
    messages.success(request, 'Product {} deleted successfully!'.format(product.name))
    return redirect('/dashboard/product/')


# Delete selected products
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_selected_product(request, product_ids):
    if request.method == 'POST':
        # Get a list of product IDs to delete
        product_ids = product_ids.split("+")
        # Delete the products
        if product_ids:
            for product_id in product_ids:
                try:
                    product = Product.objects.get(id=product_id)
                    product.delete()
                    messages.success(request, 'Product deleted successfully!')
                except ObjectDoesNotExist:
                    messages.warning(request, f'The product with ID {product_id} does not exist!')
            return redirect('/dashboard/product/')
        else:
            messages.warning(request, 'Please select at least one product to delete!')
    return redirect('/dashboard/product/')


# Product details
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def product_details(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {'product': product}
    return render(request, 'dashboard/manage_product/product_details.html', context)


# Search product
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def search_product(request):
    if request.method == 'POST':
        # get the search query from the request
        search_query = request.POST.get('search', '')
        sort_by = request.POST.get('sort_by')
        filter_by_brand = request.POST.get('filter_by_brand')
        filter_by_category = request.POST.get('filter_by_category')
        products = Product.objects.all().order_by('-sold')
        sort_price = request.POST.get('sort_price')

        if search_query:
            products = products.filter(name__icontains=search_query) | products.filter(
                category__name__icontains=search_query) | products.filter(brand__name__icontains=search_query)

        # apply brand filter if selected
        if filter_by_brand and filter_by_category:
            products = products.filter(brand__id=filter_by_brand, category__id=filter_by_category)

        elif filter_by_brand:
            products = products.filter(brand__id=filter_by_brand)
        # apply category filter if selected
        elif filter_by_category:
            products = products.filter(category__id=filter_by_category)

        # apply sorting based on selected option
        if sort_by == 'newest':
            products = products.order_by('-created_date')
        elif sort_by == 'best_seller':
            products = products.order_by('-sold')
        elif sort_by == 'most_viewed':
            products = products.order_by('-view_count')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
        elif sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')

        if sort_price == 'less_100':
            products = products.filter(price__lte=100)
        elif sort_price == '100_500':
            products = products.filter(price__gte=100, price__lte=500)
        elif sort_price == '500_1000':
            products = products.filter(price__gte=500, price__lte=1000)
        elif sort_price == '1000_2000':
            products = products.filter(price__gte=1000, price__lte=2000)
        elif sort_price == 'greater_2000':
            products = products.filter(price__gte=2000)

        if filter_by_brand:
            filter_by_brand = int(filter_by_brand)
        if filter_by_category:
            filter_by_category = int(filter_by_category)
        page_obj = paginator(request, products)
        context = {
            'products': page_obj,
            'search_query': search_query,
            'sort_by': sort_by,
            'filter_by_brand': filter_by_brand,
            'filter_by_category': filter_by_category,
            'sort_price': sort_price,
        }
        return render(request, 'dashboard/manage_product/product_table.html', context=context)
    else:
        products = Product.objects.all()
        page_object = paginator(request, products)
        context = {
            'products': page_object,
        }
        return render(request, 'dashboard/manage_product/product_table.html', context=context)


# Coupon Management
# Coupon table
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def coupon_table(request):
    # Get all coupons
    coupons = Coupon.objects.all().order_by('id')
    page_object = paginator(request, coupons)
    context = {'coupons': page_object}
    return render(request, 'dashboard/manage_coupon/coupon_table.html', context)


# Add coupon
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def add_coupon(request):
    if request.method == 'POST':
        form = AddCouponForm(request.POST)
        if form.is_valid():
            coupon = form.save()
            messages.success(request, 'Coupon {} added successfully!'.format(form.cleaned_data['code']))
            if 'save_and_add' in request.POST:
                return redirect('/dashboard/coupon/add/')
            elif 'save_and_update' in request.POST:
                return redirect('/dashboard/coupon/update/{}/'.format(coupon.id))
            else:
                return redirect('/dashboard/coupon/')
    else:
        form = AddCouponForm()
    context = {'form': form}
    return render(request, 'dashboard/manage_coupon/add_coupon.html', context)


# Update coupon
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def update_coupon(request, coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)
    if request.method == 'POST':
        form = UpdateCouponForm(request.POST, coupon=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon {} updated successfully!'.format(form.cleaned_data['code']))
            if 'save_and_add' in request.POST:
                return redirect('/dashboard/coupon/add/')
            elif 'save_and_update' in request.POST:
                return redirect('/dashboard/coupon/update/' + str(coupon.id) + '/')
            else:
                return redirect('/dashboard/coupon/')
    else:
        coupon = Coupon.objects.get(id=coupon_id)
        form = UpdateCouponForm(coupon=coupon)
    context = {'form': form}
    return render(request, 'dashboard/manage_coupon/update_coupon.html', context)


# Delete coupon
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_coupon(request, coupon_id):
    try:
        coupon = Coupon.objects.get(id=coupon_id)
    except ObjectDoesNotExist:
        messages.warning(request, 'The coupon {} you are trying to delete does not exist!'.format(coupon_id))
        return redirect('/dashboard/coupon/')
    coupon.delete()
    messages.success(request, 'Coupon {} deleted successfully!'.format(coupon.code))


# Delete selected coupons
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_selected_coupon(request, coupon_ids):
    if request.method == 'POST':
        # Get a list of coupon IDs to delete
        coupon_ids = coupon_ids.split("+")
        # Delete the coupons
        if coupon_ids:
            for coupon_id in coupon_ids:
                try:
                    coupon = Coupon.objects.get(id=coupon_id)
                    coupon.delete()
                    messages.success(request, 'Coupon deleted successfully!')
                except ObjectDoesNotExist:
                    messages.warning(request, f'The coupon with ID {coupon_id} does not exist!')
            return redirect('/dashboard/coupon/')
        else:
            messages.warning(request, 'Please select at least one coupon to delete!')
    return redirect('/dashboard/coupon/')


# Coupon details
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def coupon_details(request, coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)
    context = {'coupon': coupon}
    return render(request, 'dashboard/manage_coupon/coupon_details.html', context)


# Search coupon
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def search_coupon(request):
    search_query = request.POST.get('search', '')
    if request.method == 'POST':
        if search_query == '':
            messages.warning(request, 'Please enter a search term!')
            return redirect('/dashboard/coupon/')
        else:
            coupons = Coupon.objects.filter(
                code__icontains=search_query) | Coupon.objects.filter(
                discount__icontains=search_query) | Coupon.objects.filter(
                amount__icontains=search_query) | Coupon.objects.filter(
                is_active__icontains=search_query)
            page_object = paginator(request, coupons)

        if not coupons:
            messages.success(request, 'No coupons found {} !'.format(search_query))
    else:
        coupons = Coupon.objects.all()
        page_object = paginator(request, coupons)
    context = {'coupons': page_object,
               'search_query': search_query}
    return render(request, 'dashboard/manage_coupon/coupon_table.html', context)


# Payment Management


# Order Management
# Order table
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def order_table(request):
    # Get all orders
    orders = Orders.objects.all().order_by('-id')
    page_object = paginator(request, orders)
    context = {'orders': page_object}
    return render(request, 'dashboard/manage_order/order_table.html', context)


# Order details
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def order_details(request, order_id):
    # Get data from orders and order_details
    order = Orders.objects.get(id=order_id)
    order_details = OrderDetails.objects.filter(order=order)
    total = sum(item.sub_total for item in order_details)
    total_amount_without_coupon = sum(item.get_total_amount_without_coupon for item in order_details)
    total_amount_with_coupon = sum(item.get_total_amount_with_coupon for item in order_details)
    #  check if any coupon is applied
    if order_details.filter(coupon_applied=True).exists():
        code = order_details[0].coupon.code if order_details[0].coupon_applied is True else None
        discount = sum(item.get_discount for item in order_details)
    else:
        code = None
        discount = 0
    delivery_address = DeliveryAddress.objects.get(id=order.delivery_address.id)
    payment = Payment.objects.get(order=order)
    context = {
        'order': order,
        'order_details': order_details,
        'total': total,
        'code': code,
        'discount': discount,
        'total_amount_without_coupon': total_amount_without_coupon,
        'total_amount_with_coupon': total_amount_with_coupon,
        'delivery_address': delivery_address,
        'payment': payment,
    }

    return render(request, 'dashboard/manage_order/order_details.html', context)


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def update_order_status(request, order_id):
    order = Orders.objects.get(id=order_id)
    if request.method == 'POST':
        form = UpdateOrderStatusForm(request.POST, order=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order status updated successfully!')
            if 'save_and_update' in request.POST:
                return redirect('/dashboard/order/update_status/' + str(order.id) + '/')
            else:
                next_url = request.GET.get('next', '/dashboard/order/')
                return redirect(next_url)

    else:
        order = Orders.objects.get(id=order_id)
        form = UpdateOrderStatusForm(order=order)
    context = {'form': form}
    return render(request, 'dashboard/manage_order/update_order_status.html', context)


# Delete order
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_order(request, order_id):
    try:
        order = Orders.objects.get(id=order_id)
    except ObjectDoesNotExist:
        messages.warning(request, 'The order {} you are trying to delete does not exist!'.format(order_id))
        return redirect('/dashboard/order/')
    # Update Product Sold Count, Stock, Profit

    for order_detail in OrderDetails.objects.filter(order_id=order_id):
        product = Product.objects.get(id=order_detail.product_id)
        product.sold -= order_detail.quantity
        product.stock += order_detail.quantity
        product.profit -= (order_detail.product.price - order_detail.product.price_original) \
                          * order_detail.quantity - order_detail.discount
        product.save()

    # Delete order
    order.delete()
    messages.success(request, 'Order {} deleted successfully!'.format(order_id))
    return redirect('/dashboard/order/')


# Delete selected orders
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_selected_order(request, order_ids):
    if request.method == 'POST':
        # Get a list of order IDs to delete
        order_ids = order_ids.split("+")
        # Delete the orders
        if order_ids:
            for order_id in order_ids:
                try:
                    order = Orders.objects.get(id=order_id)
                    # Update Product Sold Count, Stock, Profit

                    for order_detail in OrderDetails.objects.filter(order_id=order_id):
                        product = Product.objects.get(id=order_detail.product_id)
                        product.sold -= order_detail.quantity
                        product.stock += order_detail.quantity
                        product.profit -= order_detail.quantity * order_detail.price
                        product.save()

                    order.delete()
                except ObjectDoesNotExist:
                    messages.warning(request, f'The order with ID {order_id} does not exist!')
            messages.success(request, 'Order deleted successfully!')
            return redirect('/dashboard/order/')
        else:
            messages.warning(request, 'Please select at least one order to delete!')
    return redirect('/dashboard/order/')


# Search order
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def search_order(request):
    search_query = request.POST.get('search', '')
    if request.method == 'POST':
        if search_query == '':
            messages.warning(request, 'Please enter a search term!')
            return redirect('/dashboard/order/')
        else:
            orders = Orders.objects.filter(
                id__icontains=search_query) | Orders.objects.filter(
                customer__user__first_name__icontains=search_query) | Orders.objects.filter(
                customer__user__last_name__icontains=search_query) | Orders.objects.filter(
                customer__user__email__icontains=search_query) | Orders.objects.filter(
                order_date__icontains=search_query) | Orders.objects.filter(
                status__icontains=search_query) | Orders.objects.filter(
                total_discount__icontains=search_query) | Orders.objects.filter(
                total_amount__icontains=search_query) | Orders.objects.filter(
                delivery_address__first_name__icontains=search_query) | Orders.objects.filter(
                delivery_address__last_name__icontains=search_query) | Orders.objects.filter(
                delivery_address__mobile__icontains=search_query) | Orders.objects.filter(
                delivery_address__address__icontains=search_query) | Orders.objects.filter(
                delivery_address__city__icontains=search_query) | Orders.objects.filter(
                delivery_address__state__icontains=search_query) | Orders.objects.filter(
                delivery_address__country__icontains=search_query) | Orders.objects.filter(
                delivery_address__zip_code__icontains=search_query)

            page_object = paginator(request, orders)

        if not orders:
            messages.success(request, 'No orders found {} !'.format(search_query))
    else:
        orders = Orders.objects.all()
        page_object = paginator(request, orders)
    context = {'orders': page_object,
               'search_query': search_query}
    return render(request, 'dashboard/manage_order/order_table.html', context)


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return


# Download invoice
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def download_invoice(request, order_id):
    order = Orders.objects.get(id=order_id)
    order_details = OrderDetails.objects.filter(order=order)
    total = sum(item.sub_total for item in order_details)
    total_amount_without_coupon = sum(item.get_total_amount_without_coupon for item in order_details)
    total_amount_with_coupon = sum(item.get_total_amount_with_coupon for item in order_details)
    #  check if any coupon is applied
    if order_details.filter(coupon_applied=True).exists():
        code = order_details[0].coupon.code if order_details[0].coupon_applied is True else None
        discount = sum(item.get_discount for item in order_details)
    else:
        code = None
        discount = 0
    delivery_address = DeliveryAddress.objects.get(id=order.delivery_address.id)
    payment = Payment.objects.get(order=order)
    context = {
        'order': order,
        'order_details': order_details,
        'total': total,
        'code': code,
        'discount': discount,
        'total_amount_without_coupon': total_amount_without_coupon,
        'total_amount_with_coupon': total_amount_with_coupon,
        'delivery_address': delivery_address,
        'payment': payment,
    }
    pdf = render_to_pdf('dashboard/manage_order/invoice.html', context)
    filename = 'LCLShop_invoice_{}.pdf'.format(order_id)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    return response


# Feedback Management
# Feedback table
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def feedback_table(request):
    # Get all feedbacks
    feedbacks = Feedback.objects.all().order_by('id')
    page_object = paginator(request, feedbacks)
    context = {'feedbacks': page_object}
    return render(request, 'dashboard/manage_feedback/feedback_table.html', context)


# Feedback details
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def feedback_details(request, feedback_id):
    # Get data from feedbacks and feedback_details
    feedback = Feedback.objects.get(id=feedback_id)
    context = {'feedback': feedback}
    return render(request, 'dashboard/manage_feedback/feedback_details.html', context)


# Delete feedback
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_feedback(request, feedback_id):
    try:
        feedback = Feedback.objects.get(id=feedback_id)
    except ObjectDoesNotExist:
        messages.warning(request, 'The feedback {} you are trying to delete does not exist!'.format(feedback_id))
        return redirect('/dashboard/feedback/')
    feedback.delete()
    messages.success(request, 'Feedback {} deleted successfully!'.format(feedback_id))
    return redirect('/dashboard/feedback/')


# Delete selected feedbacks
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_selected_feedback(request, feedback_ids):
    if request.method == 'POST':
        # Get a list of feedback IDs to delete
        feedback_ids = feedback_ids.split("+")
        # Delete the feedbacks
        if feedback_ids:
            for feedback_id in feedback_ids:
                try:
                    feedback = Feedback.objects.get(id=feedback_id)
                    feedback.delete()
                    messages.success(request, 'Feedback deleted successfully!')
                except ObjectDoesNotExist:
                    messages.warning(request, f'The feedback with ID {feedback_id} does not exist!')
            return redirect('/dashboard/feedback/')
        else:
            messages.warning(request, 'Please select at least one feedback to delete!')
    return redirect('/dashboard/feedback/')


# Search feedback
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def search_feedback(request):
    search_query = request.POST.get('search', '')
    if request.method == 'POST':
        if search_query == '':
            messages.warning(request, 'Please enter a search term!')
            return redirect('/dashboard/feedback/')
        else:
            feedbacks = Feedback.objects.filter(
                id__icontains=search_query) | Feedback.objects.filter(
                name__icontains=search_query) | Feedback.objects.filter(
                email__icontains=search_query) | Feedback.objects.filter(
                subject__icontains=search_query) | Feedback.objects.filter(
                message__icontains=search_query) | Feedback.objects.filter(
                mobile__icontains=search_query) | Feedback.objects.filter(
                date_sent__icontains=search_query)
            page_object = paginator(request, feedbacks)

        if not feedbacks:
            messages.success(request, 'No feedbacks found {} !'.format(search_query))
    else:
        feedbacks = Feedback.objects.all()
        page_object = paginator(request, feedbacks)
    context = {'feedbacks': page_object,
               'search_query': search_query}
    return render(request, 'dashboard/manage_feedback/feedback_table.html', context)


# Export Customer
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_customer_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Mobile', 'Address', 'Customer Image', 'Last Login',
         'Date Joined', 'Active', 'Admin'])

    customers = Customer.objects.all().order_by('id')
    for customer in customers:
        writer.writerow([customer.user.id if customer.user.id else '',
                         customer.user.username if customer.user.username else '',
                         customer.user.first_name if customer.user.first_name else '',
                         customer.user.last_name if customer.user.last_name else '',
                         customer.user.email if customer.user.email else '',
                         customer.mobile.strip('+').lstrip('0') if customer.mobile else '',
                         customer.address if customer.address else '',
                         customer.customer_image.url if customer.customer_image else '',
                         customer.user.last_login.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                                        '') if customer.user.last_login else '',
                         customer.user.date_joined.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                                         '') if customer.user.date_joined else '',
                         customer.user.is_active if customer.user.is_active else 'False',
                         customer.user.is_superuser if customer.user.is_superuser else 'False'])

    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_customer_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="customers.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Customers')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Mobile', 'Address', 'Customer Image',
               'Last Login', 'Date Joined', 'Active', 'Admin']

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)

    font_style = xlwt.XFStyle()

    customers = Customer.objects.all().order_by('id')

    for customer in customers:
        row_num += 1
        row = [
            customer.user.id if customer.user.id else '',
            customer.user.username if customer.user.username else '',
            customer.user.first_name if customer.user.first_name else '',
            customer.user.last_name if customer.user.last_name else '',
            customer.user.email if customer.user.email else '',
            customer.mobile.strip('+').lstrip('0') if customer.mobile else '',
            customer.address if customer.address else '',
            customer.customer_image.url if customer.customer_image else '',
            customer.user.last_login.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                           '') if customer.user.last_login else '',
            customer.user.date_joined.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                            '') if customer.user.date_joined else '',
            customer.user.is_active if customer.user.is_active else 'False',
            customer.user.is_superuser if customer.user.is_superuser else 'False',
        ]
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, cell_value, font_style)

    wb.save(response)
    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_customer_json(request):
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="customers.json"'

    customers = Customer.objects.all().order_by('id')

    data = []
    for customer in customers:
        customer_data = {
            'id': customer.user.id if customer.user.id else '',
            'username': customer.user.username if customer.user.username else '',
            'first_name': customer.user.first_name if customer.user.first_name else '',
            'last_name': customer.user.last_name if customer.user.last_name else '',
            'email': customer.user.email if customer.user.email else '',
            'mobile': customer.mobile.strip('+').lstrip('0') if customer.mobile else '',
            'address': customer.address if customer.address else '',
            'customer_image': customer.customer_image.url if customer.customer_image else '',
            'last_login': customer.user.last_login.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                                         '') if customer.user.last_login else '',
            'date_joined': customer.user.date_joined.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                                           '') if customer.user.date_joined else '',
            'is_active': customer.user.is_active if customer.user.is_active else False,
            'is_superuser': customer.user.is_superuser if customer.user.is_superuser else False,
        }
        data.append(customer_data)

    json.dump(data, response, indent=4)

    return response


# Category Export
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_category_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="categories.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Category Slug', 'Category Name', 'Category Description'])

    categories = Category.objects.all().order_by('id')
    for category in categories:
        writer.writerow([category.id if category.id else '',
                         category.slug if category.slug else '',
                         category.name if category.name else '',
                         category.description if category.description else ''])
    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_category_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="categories.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Categories')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'Category Slug', 'Category Name', 'Category Description']

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)

    font_style = xlwt.XFStyle()

    categories = Category.objects.all().order_by('id')

    for category in categories:
        row_num += 1
        row = [
            category.id if category.id else '',
            category.slug if category.slug else '',
            category.name if category.name else '',
            category.description if category.description else '',
        ]
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, cell_value, font_style)

    wb.save(response)
    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_category_json(request):
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="categories.json"'

    categories = Category.objects.all().order_by('id')

    data = []
    for category in categories:
        category_data = {
            'id': category.id if category.id else '',
            'slug': category.slug if category.slug else '',
            'name': category.name if category.name else '',
            'description': category.description if category.description else '',
        }
        data.append(category_data)

    json.dump(data, response, indent=4)

    return response


# Brand Export
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_brand_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="brands.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Brand Slug', 'Brand Name', 'Brand Description', 'Brand Logo Image'])

    brands = Brand.objects.all().order_by('id')
    for brand in brands:
        writer.writerow([brand.id if brand.id else '',
                         brand.slug if brand.slug else '',
                         brand.name if brand.name else '',
                         brand.description if brand.description else '',
                         brand.logo.url if brand.logo else ''])

    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_brand_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="brands.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Brands')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'Brand Slug', 'Brand Name', 'Brand Description', 'Brand Logo Image']

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)

    font_style = xlwt.XFStyle()

    brands = Brand.objects.all().order_by('id')

    for brand in brands:
        row_num += 1
        row = [
            brand.id if brand.id else '',
            brand.slug if brand.slug else '',
            brand.name if brand.name else '',
            brand.description if brand.description else '',
            brand.logo.url if brand.logo else '',
        ]
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, cell_value, font_style)

    wb.save(response)
    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_brand_json(request):
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="brands.json"'

    brands = Brand.objects.all().order_by('id')

    data = []
    for brand in brands:
        brand_data = {
            'id': brand.id if brand.id else '',
            'slug': brand.slug if brand.slug else '',
            'name': brand.name if brand.name else '',
            'description': brand.description if brand.description else '',
            'brand_logo': brand.logo.url if brand.logo else '',
        }
        data.append(brand_data)

    json.dump(data, response, indent=4)

    return response


# Coupon Export
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_coupon_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="coupons.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ['ID', 'Coupon Code', 'Coupon Discount', 'Coupon Amount', 'Valid From', 'Valid To', 'Coupon Status'])

    coupons = Coupon.objects.all().order_by('id')
    for coupon in coupons:
        writer.writerow([coupon.id if coupon.id else '',
                         coupon.code if coupon.code else '',
                         float(coupon.discount) if coupon.discount else '',
                         coupon.amount if coupon.amount else '',
                         coupon.valid_from.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                                 '') if coupon.valid_from else '',
                         coupon.valid_to.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00', '') if coupon.valid_to else '',
                         coupon.is_active if coupon.is_active else 'False'])
    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_coupon_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="coupons.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Coupons')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'Coupon Code', 'Coupon Discount', 'Coupon Amount', 'Valid From', 'Valid To', 'Coupon Status']

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)

    font_style = xlwt.XFStyle()

    coupons = Coupon.objects.all().order_by('id')

    for coupon in coupons:
        row_num += 1
        row = [
            coupon.id if coupon.id else '',
            coupon.code if coupon.code else '',
            float(coupon.discount) if coupon.discount else '',
            coupon.amount if coupon.amount else '',
            coupon.valid_from.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00', '') if coupon.valid_from else '',
            coupon.valid_to.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00', '') if coupon.valid_to else '',
            coupon.is_active if coupon.is_active else 'False',
        ]
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, cell_value, font_style)

    wb.save(response)
    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_coupon_json(request):
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="coupons.json"'

    coupons = Coupon.objects.all().order_by('id')

    data = []
    for coupon in coupons:
        coupon_data = {
            'id': coupon.id if coupon.id else '',
            'code': coupon.code if coupon.code else '',
            'discount': float(coupon.discount) if coupon.discount else '',
            'amount': coupon.amount if coupon.amount else '',
            'valid_from': coupon.valid_from.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00' or '+00:00',
                                                                                  '') if coupon.valid_from else '',
            'valid_to': coupon.valid_to.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00' or '+00:00',
                                                                              '') if coupon.valid_to else '',
            'is_active': coupon.is_active if coupon.is_active else 'False',
        }
        data.append(coupon_data)

    json.dump(data, response, indent=4)

    return response


#  Product Export
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_product_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ['ID', 'Product Name', 'Product Slug', 'Category', 'Brand', ' Price Original',
         'Price', 'Old Price', 'Stock', 'Product Image', 'Sold', 'Created Date', 'Updated Date'])

    products = Product.objects.all().order_by('id')
    for product in products:
        writer.writerow([product.id if product.id else '',
                         product.name if product.name else '',
                         product.slug if product.slug else '',
                         product.category.name if product.category else '',
                         product.brand.name if product.brand else '',
                         float(product.price_original) if product.price_original else '',
                         float(product.price) if product.price else '',
                         float(product.old_price) if product.old_price else '',
                         product.stock if product.stock else '',
                         product.product_image.url if product.product_image else '',
                         product.sold if product.sold else '',
                         product.created_date.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                                    '') if product.created_date else '',
                         product.updated_date.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                                    '') if product.updated_date else ''])

    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_product_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="products.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Products')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'Product Name', 'Product Slug', 'Category', 'Brand', ' Price Original',
               'Price', 'Old Price', 'Stock', 'Product Image', 'Sold', 'Created Date', 'Updated Date']

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)

    font_style = xlwt.XFStyle()

    products = Product.objects.all().order_by('id')

    for product in products:
        row_num += 1
        row = [
            product.id if product.id else '',
            product.name if product.name else '',
            product.slug if product.slug else '',
            product.category.name if product.category else '',
            product.brand.name if product.brand else '',
            float(product.price_original) if product.price_original else '',
            float(product.price) if product.price else '',
            float(product.old_price) if product.old_price else '',
            product.stock if product.stock else '',
            product.product_image.url if product.product_image else '',
            product.sold if product.sold else '',
            product.created_date.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00', '') if product.created_date else '',
            product.updated_date.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00', '') if product.updated_date else '',
        ]
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, cell_value, font_style)

    wb.save(response)
    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_product_json(request):
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="products.json"'

    products = Product.objects.all().order_by('id')

    data = []
    for product in products:
        product_data = {
            'id': product.id if product.id else '',
            'name': product.name if product.name else '',
            'slug': product.slug if product.slug else '',
            'category': product.category.name if product.category else '',
            'brand': product.brand.name if product.brand else '',
            'price_original': float(product.price_original) if product.price_original else '',
            'price': float(product.price) if product.price else '',
            'old_price': float(product.old_price) if product.old_price else '',
            'stock': product.stock if product.stock else '',
            'product_image': product.product_image.url if product.product_image else '',
            'sold': product.sold if product.sold else '',
            'created_date': product.created_date.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                                       '') if product.created_date else '',
            'updated_date': product.updated_date.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                                       '') if product.updated_date else '',
        }
        data.append(product_data)

    json.dump(data, response, indent=4)

    return response


# Feedback Export
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_feedback_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="feedbacks.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Mobile', 'Subject', 'Message', 'Date Sent'])

    feedbacks = Feedback.objects.all().order_by('id')
    for feedback in feedbacks:
        writer.writerow([feedback.id if feedback.id else '',
                         feedback.name if feedback.name else '',
                         feedback.email if feedback.email else '',
                         feedback.mobile if feedback.mobile else '',
                         feedback.subject if feedback.subject else '',
                         feedback.message if feedback.message else '',
                         feedback.date_sent.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                                  '') if feedback.date_sent else ''])

    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_feedback_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="feedbacks.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Feedbacks')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'Name', 'Email', 'Mobile', 'Subject', 'Message', 'Date Sent']

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)

    font_style = xlwt.XFStyle()

    feedbacks = Feedback.objects.all().order_by('id')

    for feedback in feedbacks:
        row_num += 1
        row = [
            feedback.id if feedback.id else '',
            feedback.name if feedback.name else '',
            feedback.email if feedback.email else '',
            feedback.mobile if feedback.mobile else '',
            feedback.subject if feedback.subject else '',
            feedback.message if feedback.message else '',
            feedback.date_sent.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00', '') if feedback.date_sent else '',
        ]
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, cell_value, font_style)

    wb.save(response)
    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_feedback_json(request):
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="feedbacks.json"'

    feedbacks = Feedback.objects.all().order_by('id')

    data = []
    for feedback in feedbacks:
        feedback_data = {
            'id': feedback.id if feedback.id else '',
            'name': feedback.name if feedback.name else '',
            'email': feedback.email if feedback.email else '',
            'mobile': feedback.mobile if feedback.mobile else '',
            'subject': feedback.subject if feedback.subject else '',
            'message': feedback.message if feedback.message else '',
            'date_sent': feedback.date_sent.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                                  '') if feedback.date_sent else '',
        }
        data.append(feedback_data)

    json.dump(data, response, indent=4)

    return response


# Payment Export
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_payment_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Order ID', 'Payment Method', 'Payment Status', 'Total', 'Transaction ID',
                     'Payment Date'])

    payments = Payment.objects.all().order_by('id')

    for payment in payments:
        writer.writerow([
            payment.id if payment.id else '',
            payment.customer.user.username if payment.customer.user.username else '',
            payment.order.id if payment.order.id else '',
            payment.payment_method if payment.payment_method else '',
            payment.payment_status if payment.payment_status else '',
            payment.total if payment.total else 0,
            payment.transaction_id if payment.transaction_id else '',
            payment.payment_date.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00', '') if payment.payment_date else '',
        ])

    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_payment_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="payments.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Payments')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'Username', 'Order ID', 'Payment Method', 'Payment Status', 'Total', 'Transaction ID',
               'Payment Date']

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)

    font_style = xlwt.XFStyle()

    payments = Payment.objects.all().order_by('id')

    for payment in payments:
        row_num += 1
        row = [
            payment.id if payment.id else '',
            payment.customer.user.username if payment.customer.user.username else '',
            payment.order.id if payment.order.id else '',
            payment.payment_method if payment.payment_method else '',
            payment.payment_status if payment.payment_status else '',
            payment.total if payment.total else 0,
            payment.transaction_id if payment.transaction_id else '',
            payment.payment_date.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00', '') if payment.payment_date else '',
        ]
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, cell_value, font_style)

    wb.save(response)
    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_payment_json(request):
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="payments.json"'

    payments = Payment.objects.all().order_by('id')

    data = []
    for payment in payments:
        payment_data = {
            'id': payment.id if payment.id else '',
            'username': payment.customer.user.username if payment.customer.user.username else '',
            'order_id': payment.order.id if payment.order.id else '',
            'payment_method': payment.payment_method if payment.payment_method else '',
            'payment_status': payment.payment_status if payment.payment_status else '',
            'total': float(payment.total) if payment.total else 0,
            'transaction_id': payment.transaction_id if payment.transaction_id else '',
            'payment_date': payment.payment_date.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                                       '') if payment.payment_date else '',
        }
        data.append(payment_data)

    json.dump(data, response, indent=4)

    return response


# Review Export
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_review_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reviews.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Full Name', 'Product Name', 'Rating', 'Message Review', 'Date Added',
                     'Date Update', 'Review Status'])

    reviews = Review.objects.all().order_by('id')

    for review in reviews:
        writer.writerow([
            review.id if review.id else '',
            review.customer.user.username if review.customer.user.username else '',
            review.name if review.name else '',
            review.product.name if review.product.name else '',
            review.rate if review.rate else '',
            review.message_review if review.message_review else '',
            review.date_added.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00', '') if review.date_added else '',
            review.date_updated.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00', '') if review.date_updated else '',
            review.review_status if review.review_status else '',
        ])

    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_review_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="reviews.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Reviews')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'Username', 'Full Name', 'Product Name', 'Rating', 'Message Review', 'Date Added',
               'Date Update', 'Review Status']

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)

    font_style = xlwt.XFStyle()

    reviews = Review.objects.all().order_by('id')

    for review in reviews:
        row_num += 1
        row = [
            review.id if review.id else '',
            review.customer.user.username if review.customer.user.username else '',
            review.name if review.name else '',
            review.product.name if review.product.name else '',
            review.rate if review.rate else '',
            review.message_review if review.message_review else '',
            review.date_added.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00', '') if review.date_added else '',
            review.date_updated.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00', '') if review.date_updated else '',
            review.review_status if review.review_status else '',
        ]
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, cell_value, font_style)

    wb.save(response)
    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_review_json(request):
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="reviews.json"'

    reviews = Review.objects.all().order_by('id')

    data = []
    for review in reviews:
        review_data = {
            'id': review.id if review.id else '',
            'username': review.customer.user.username if review.customer.user.username else '',
            'full_name': review.name if review.name else '',
            'product_name': review.product.name if review.product.name else '',
            'rate': review.rate if review.rate else '',
            'message_review': review.message_review if review.message_review else '',
            'date_added': review.date_added.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                                  '') if review.date_added else '',
            'date_updated': review.date_updated.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                                      '') if review.date_updated else '',
            'review_status': review.review_status if review.review_status else '',
        }
        data.append(review_data)

    json.dump(data, response, indent=4)

    return response


# Order Export
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_order_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Order Date', 'Order Status', 'Sub Total', 'Total Discount', 'Total Amount'])

    orders = Orders.objects.all().order_by('id')

    for order in orders:
        writer.writerow([
            order.id if order.id else '',
            order.customer.user.username if order.customer.user.username else '',
            order.order_date.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00', '') if order.order_date else '',
            order.status if order.status else '',
            order.sub_total if order.sub_total else 0,
            order.total_discount if order.total_discount else 0,
            order.total_amount if order.total_amount else 0,
        ])

    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_order_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="orders.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Orders')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'Username', 'Order Date', 'Order Status', 'Sub Total', 'Total Discount', 'Total Amount']

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)

    font_style = xlwt.XFStyle()

    orders = Orders.objects.all().order_by('id')

    for order in orders:
        row_num += 1
        row = [
            order.id if order.id else '',
            order.customer.user.username if order.customer.user.username else '',
            order.order_date.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00', '') if order.order_date else '',
            order.status if order.status else '',
            order.sub_total if order.sub_total else 0,
            order.total_discount if order.total_discount else 0,
            order.total_amount if order.total_amount else 0,
        ]
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, cell_value, font_style)

    wb.save(response)
    return response


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def export_order_json(request):
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="orders.json"'

    orders = Orders.objects.all().order_by('id')

    data = []
    for order in orders:
        order_data = {
            'id': order.id if order.id else '',
            'username': order.customer.user.username if order.customer.user.username else '',
            'order_date': order.order_date.strftime('%Y-%m-%d %H:%M:%S').replace('+00:00',
                                                                                 '') if order.order_date else '',
            'status': order.status if order.status else '',
            'sub_total': float(order.sub_total) if order.sub_total else 0,
            'total_discount': float(order.total_discount) if order.total_discount else 0,
            'total_amount': float(order.total_amount) if order.total_amount else 0,
        }
        data.append(order_data)

    json.dump(data, response, indent=4)

    return response


# Payment Management
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def payment_table(request):
    payments = Payment.objects.all().order_by('-id')
    page_object = paginator(request, payments)

    context = {
        'payments': page_object,
    }
    return render(request, 'dashboard/manage_payment/payment_table.html', context)


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def payment_details(request, payment_id):
    payment = Payment.objects.get(id=payment_id)
    context = {
        'payment': payment,
    }
    return render(request, 'dashboard/manage_payment/payment_details.html', context)


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def search_payment(request):
    if request.method == 'POST':
        search_query = request.POST.get('search', '')
        payments = Payment.objects.filter(customer__user__username__icontains=search_query) | Payment.objects.filter(
            order__id__icontains=search_query) | Payment.objects.filter(
            payment_method__icontains=search_query) | Payment.objects.filter(
            payment_status__icontains=search_query) | Payment.objects.filter(
            payment_date__icontains=search_query).order_by('-id')
        page_object = paginator(request, payments)

        context = {
            'payments': page_object,
            'search_query': search_query,
        }
        return render(request, 'dashboard/manage_payment/payment_table.html', context)
    else:
        return redirect('/dashboard/payment/')


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def update_payment_status(request, payment_id):
    payment = Payment.objects.get(id=payment_id)
    if request.method == 'POST':
        form = UpdatePaymentStatusForm(request.POST, payment=payment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment status has been updated successfully.')
            if 'save_and_update' in request.POST:
                return redirect('/dashboard/payment/update_status/{}/'.format(payment_id))
            else:
                next_url = request.GET.get('next', '/dashboard/payment/')
                return redirect(next_url)
    else:
        form = UpdatePaymentStatusForm(payment=payment)
    context = {
        'form': form,
        'payment': payment,
    }
    return render(request, 'dashboard/manage_payment/update_payment_status.html', context)


# Review Management
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def review_table(request):
    reviews = Review.objects.all().order_by('-id')
    page_object = paginator(request, reviews)
    context = {
        'reviews': page_object}
    return render(request, 'dashboard/manage_review/review_table.html', context)


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def review_details(request, review_id):
    review = Review.objects.get(id=review_id)
    context = {
        'review': review,
    }
    return render(request, 'dashboard/manage_review/review_details.html', context)


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_review(request, review_id):
    review = Review.objects.get(id=review_id)
    review.delete()
    # Update product rate
    review_rate_average = Review.objects.filter(product=review.product).aggregate(Avg('rate'))
    review.product.review_rate_average = review_rate_average.get('rate__avg', 0) or 0
    # Update product review count
    review.product.review_count = Review.objects.filter(product=review.product).count()
    review.product.save()
    messages.success(request, 'Review has been deleted successfully.')
    return redirect('/dashboard/review/')


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def delete_selected_review(request, review_ids):
    if request.method == 'POST':
        # Get a list of user IDs to delete
        review_ids = review_ids.split('+')
        if review_ids:
            for review_id in review_ids:
                try:
                    review = Review.objects.get(id=review_id)
                    review.delete()
                    # Update product rate
                    review_rate_average = Review.objects.filter(product=review.product).aggregate(Avg('rate'))
                    review.product.review_rate_average = review_rate_average.get('rate__avg', 0) or 0
                    # Update product review count
                    review.product.review_count = Review.objects.filter(product=review.product).count()
                    review.product.save()
                    messages.success(request, f'Review with ID {review_id} has been deleted successfully.')
                except ObjectDoesNotExist:
                    messages.warning(request, f'Review with ID {review_id} does not exist!')
            return redirect('/dashboard/review/')
        else:
            messages.warning(request, 'Please select at least one review to delete.')
    return redirect('/dashboard/review/')


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def search_review(request):
    if request.method == 'POST':
        search_query = request.POST.get('search')
        if search_query is not None:
            reviews = Review.objects.filter(customer__user__username__icontains=search_query) | Review.objects.filter(
                product__name__icontains=search_query) | Review.objects.filter(
                message_review__icontains=search_query) | Review.objects.filter(
                review_status__icontains=search_query)
            page_object = paginator(request, reviews)



        else:
            reviews = Review.objects.all()
            page_object = paginator(request, reviews)

        context = {
            'reviews': page_object,
            'search_query': search_query
        }
        return render(request, 'dashboard/manage_review/review_table.html', context)
    else:
        return redirect('/dashboard/review/')


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def change_review_status(request, review_id):
    review = Review.objects.get(id=review_id)
    if review.review_status:
        review.review_status = False
        review.save()
        # Update product rate
        review_rate_average = Review.objects.filter(product=review.product, review_status=True).aggregate(Avg('rate'))
        review.product.review_rate_average = review_rate_average.get('rate__avg', 0) or 0
        # Update product review count
        review.product.review_count = Review.objects.filter(product=review.product, review_status=True).count()
        review.product.save()
        messages.success(request, 'Review status has been changed to Pending.')
        return redirect('/dashboard/review/')

    else:
        review.review_status = True
        review.save()
        # Update product rate
        review_rate_average = Review.objects.filter(product=review.product, review_status=True).aggregate(
            Avg('rate')) or 0
        review.product.review_rate_average = review_rate_average.get('rate__avg', 0) or 0
        # Update product review count
        review.product.review_count = Review.objects.filter(product=review.product, review_status=True).count() or 0
        review.product.save()
        messages.success(request, 'Review status has been changed to Approve.')
        return redirect('/dashboard/review/')


# Sale Statistics
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def sales_statistics(request):
    # get all recent customers last login
    users = User.objects.filter(is_superuser=False, is_staff=False, is_active=True).order_by('last_login')[:10]

    customers = Customer.objects.all()

    # get all recent orders
    orders = Orders.objects.all()

    payments = Payment.objects.all()
    # get all recent sales
    sales = 0
    for order in orders:
        sales += order.total_amount
    # get revenue = sold * (price original - price sale - discount)
    profit = 0
    for order in orders:
        profit += order.profit_order

    # quality product sale
    quality_product_sale = 0
    for order in orders:
        for order_detail in order.orderdetails_set.all():
            quality_product_sale += order_detail.quantity
    # get all product sold count
    product_sold_count = 0
    for product in Product.objects.all():
        product_sold_count += product.sold

    number_customer = User.objects.filter(is_superuser=False, is_staff=False, is_active=True).count()

    # get all view_count of product
    view_count = 0
    for product in Product.objects.all():
        view_count += product.view_count

    # total customers
    total_customers = User.objects.filter(is_superuser=False, is_staff=False, is_active=True).count()
    # total orders
    total_orders = Orders.objects.all().count()
    # total products
    total_products = Product.objects.all().count()
    # total discounts used by customers
    total_discounts = 0
    for order in Orders.objects.all():
        total_discounts += order.total_discount

    # Profit Ratio
    total_profit_ratio = profit / sales * 100
    # Just get one decimal
    total_profit_ratio = round(total_profit_ratio, 1)
    # total feedback
    total_feedback = Feedback.objects.all().count()
    # total review
    total_review = Review.objects.all().count()
    # total payment
    total_payment = Payment.objects.all().count()
    # total review rate
    total_review_rate = Review.objects.all().aggregate(Avg('rate'))
    total_review_rate = total_review_rate['rate__avg']
    # Just get one decimal
    total_review_rate = round(total_review_rate, 1)

    # Top 10 Best Selling Products
    top_10_best_selling_products = Product.objects.all().order_by('-sold')[:10]

    # Top 10 Profitable Products
    top_10_profitable_products = Product.objects.all().order_by('-profit')[:10]

    # Top 10 Most Viewed Products
    top_10_most_viewed_products = Product.objects.all().order_by('-view_count')[:10]

    # Top 10 Rated Products
    top_10_rated_products = Product.objects.all().order_by('-review_rate_average')[:10]

    # Chart
    data_profit = Orders.objects.annotate(month=TruncMonth('order_date')).values('month').annotate(
        total_profit=Sum('profit_order')).order_by('month')
    labels = [d['month'].strftime('%B %Y') for d in data_profit]
    profit_values = [d['total_profit'] for d in data_profit]
    profit_values = [float(i) for i in profit_values]

    # Sales values
    data_sales = Orders.objects.annotate(month=TruncMonth('order_date')).values('month').annotate(
        total_sales=Sum('total_amount')).order_by('month')
    sales_values = [d['total_sales'] for d in data_sales]
    sales_values = [float(i) for i in sales_values]

    # Forecasted sales for next month
    last_month = data_sales[len(data_sales) - 1]['month']
    next_month = last_month + pd.DateOffset(months=1)
    next_month_label = next_month.strftime('%B %Y')
    data_df = pd.DataFrame({'sales': sales_values}, index=pd.to_datetime(labels, format='%B %Y'))
    data_df = data_df.asfreq('MS')
    fit = ExponentialSmoothing(data_df).fit()
    forecast = fit.forecast(1)
    next_month_sales = forecast[0]
    next_month_sales = float(next_month_sales)
    # round it to 1 decimal
    next_month_sales = round(next_month_sales, 1)
    sales_values.append(next_month_sales)

    # Forecasted profit for next month
    last_month = data_profit[len(data_profit) - 1]['month']
    next_month = last_month + pd.DateOffset(months=1)
    next_month_label = next_month.strftime('%B %Y')
    data_df = pd.DataFrame({'profit': profit_values}, index=pd.to_datetime(labels, format='%B %Y'))
    data_df = data_df.asfreq('MS')
    fit = ExponentialSmoothing(data_df).fit()
    forecast = fit.forecast(1)
    next_month_revenue = forecast[0]
    # convert to float
    next_month_revenue = float(next_month_revenue)
    # round it to 1 decimal
    next_month_revenue = round(next_month_revenue, 1)
    profit_values.append(next_month_revenue)

    # Add forecasted revenue label to labels list
    labels.append(next_month_label + ' (Forecasted)')

    # list year for filter
    list_year = []
    for order in Orders.objects.all():
        list_year.append(order.order_date.year)
    list_year = list(set(list_year))
    list_year.sort(reverse=True)

    # list month for filter
    list_month = []
    for order in Orders.objects.all():
        list_month.append(order.order_date.month)
    list_month = list(set(list_month))
    list_month.sort(reverse=True)

    context = {
        'users': users,
        'customers': customers,
        'sales': sales,
        'profit': profit,
        'view_count': view_count,
        'quality_product_sale': quality_product_sale,
        'product_sold_count': product_sold_count,
        'number_customer': number_customer,
        'payments': payments,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_discounts': total_discounts,
        'total_profit_ratio': total_profit_ratio,
        'total_feedback': total_feedback,
        'total_review': total_review,
        'total_payment': total_payment,
        'total_review_rate': total_review_rate,
        'orders': orders,
        'labels': labels,
        'profit_values': profit_values,
        'sales_values': sales_values,
        'top_10_best_selling_products': top_10_best_selling_products,
        'top_10_profitable_products': top_10_profitable_products,
        'top_10_most_viewed_products': top_10_most_viewed_products,
        'top_10_rated_products': top_10_rated_products,
        'list_year': list_year,
        'list_month': list_month,
    }
    return render(request, 'dashboard/sales_statistics/sales_statistics.html', context)


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def sales_statistics_filter(request):
    if request.method == 'POST':

        # apply filters
        start_datetime = request.POST.get('start_datetime')
        end_datetime = request.POST.get('end_datetime')
        month = request.POST.get('month')
        year = request.POST.get('year')

        if month != 'all' and year != 'all' and month != '' and year != '':
            orders = Orders.objects.filter(order_date__month=month, order_date__year=year)
            reviews = Review.objects.filter(date_added__month=month, date_added__year=year)
            payments = Payment.objects.filter(payment_date__month=month, payment_date__year=year)
            feedbacks = Feedback.objects.filter(date_sent__month=month, date_sent__year=year)
            users = User.objects.filter(date_joined__month=month, date_joined__year=year, is_staff=False,
                                        is_superuser=False, is_active=True)
            messages.success(request, 'Data filtered successfully')
        elif month == 'all' and year != 'all' and year != '':
            orders = Orders.objects.filter(order_date__year=year)
            reviews = Review.objects.filter(date_added__year=year)
            payments = Payment.objects.filter(payment_date__year=year)
            feedbacks = Feedback.objects.filter(date_sent__year=year)
            users = User.objects.filter(date_joined__year=year, is_staff=False, is_superuser=False, is_active=True)
            messages.success(request, 'Data filtered successfully')
        elif month != 'all' and year == 'all' and month != '':
            orders = Orders.objects.filter(order_date__month=month)
            reviews = Review.objects.filter(date_added__month=month)
            payments = Payment.objects.filter(payment_date__month=month)
            feedbacks = Feedback.objects.filter(date_sent__month=month)
            users = User.objects.filter(date_joined__month=month, is_staff=False, is_superuser=False, is_active=True)
            messages.success(request, 'Data filtered successfully')
        elif start_datetime != '' and end_datetime != '':
            orders = Orders.objects.filter(order_date__range=(start_datetime, end_datetime))
            reviews = Review.objects.filter(date_added__range=(start_datetime, end_datetime))
            payments = Payment.objects.filter(payment_date__range=(start_datetime, end_datetime))
            feedbacks = Feedback.objects.filter(date_sent__range=(start_datetime, end_datetime))
            users = User.objects.filter(date_joined__range=(start_datetime, end_datetime), is_staff=False,
                                        is_superuser=False, is_active=True)
            messages.success(request, 'Data filtered successfully')
        elif start_datetime != '' and end_datetime == '':
            orders = Orders.objects.filter(order_date__gte=start_datetime)
            reviews = Review.objects.filter(date_added__gte=start_datetime)
            payments = Payment.objects.filter(payment_date__gte=start_datetime)
            feedbacks = Feedback.objects.filter(date_sent__gte=start_datetime)
            users = User.objects.filter(date_joined__gte=start_datetime, is_staff=False, is_superuser=False,
                                        is_active=True)
            messages.success(request, 'Data filtered successfully')
        elif start_datetime == '' and end_datetime != '':
            orders = Orders.objects.filter(order_date__lte=end_datetime)
            reviews = Review.objects.filter(date_added__lte=end_datetime)
            payments = Payment.objects.filter(payment_date__lte=end_datetime)
            feedbacks = Feedback.objects.filter(date_sent__lte=end_datetime)
            users = User.objects.filter(date_joined__lte=end_datetime, is_staff=False, is_superuser=False,
                                        is_active=True)
            messages.success(request, 'Data filtered successfully')
        else:
            messages.warning(request, 'Please select a filter')
            orders = Orders.objects.all()
            reviews = Review.objects.all()
            payments = Payment.objects.all()
            feedbacks = Feedback.objects.all()
            users = User.objects.filter(is_staff=False, is_superuser=False, is_active=True)

        if orders.count() == 0:
            messages.warning(request, 'No data for this filter')
            orders = Orders.objects.all()
            reviews = Review.objects.all()
            payments = Payment.objects.all()
            feedbacks = Feedback.objects.all()
            users = User.objects.filter(is_staff=False, is_superuser=False, is_active=True)

        sales = 0
        for order in orders:
            sales += order.total_amount
        # get revenue = sold * (price original - price sale - discount)
        profit = 0
        for order in orders:
            profit += order.profit_order

        # Profit Ratio
        total_profit_ratio = profit / sales * 100
        # Just get one decimal
        total_profit_ratio = round(total_profit_ratio, 1)
        # total orders
        total_orders = orders.count()
        # total discounts used by customers
        total_discounts = 0
        for order in orders:
            total_discounts += order.total_discount

        # quality product sale
        quality_product_sale = 0
        for order in orders:
            for order_detail in order.orderdetails_set.all():
                quality_product_sale += order_detail.quantity

        # total customers
        total_customers = users.count()

        # total feedback
        total_feedback = feedbacks.count()
        # total review
        total_review = reviews.count()
        # total payment
        total_payment = payments.count()

        # total review rate
        total_review_rate = reviews.aggregate(Avg('rate'))
        total_review_rate = total_review_rate['rate__avg']

        # Just get one decimal
        if total_review_rate is not None:
            total_review_rate = round(total_review_rate, 1)
        else:
            total_review_rate = 0

        # total products
        total_products = Product.objects.all().count()
        # get all product sold count
        product_sold_count = 0
        for order in orders:
            for order_detail in order.orderdetails_set.all():
                product_sold_count += order_detail.quantity

        number_customer = users.count()

        # get all view_count of product
        view_count = 0
        for product in Product.objects.all():
            view_count += product.view_count

        # Top 10 Best Selling Products
        top_10_best_selling_products = Product.objects.all().order_by('-sold')[:10]

        # Top 10 Profitable Products
        top_10_profitable_products = Product.objects.all().order_by('-profit')[:10]

        # Top 10 Most Viewed Products
        top_10_most_viewed_products = Product.objects.all().order_by('-view_count')[:10]

        # Top 10 Rated Products
        top_10_rated_products = Product.objects.all().order_by('-review_rate_average')[:10]

        # Chart
        data_profit = Orders.objects.annotate(month=TruncMonth('order_date')).values('month').annotate(
            total_profit=Sum('profit_order')).order_by('month')
        labels = [d['month'].strftime('%B %Y') for d in data_profit]
        profit_values = [d['total_profit'] for d in data_profit]
        profit_values = [float(i) for i in profit_values]

        # Sales values
        data_sales = Orders.objects.annotate(month=TruncMonth('order_date')).values('month').annotate(
            total_sales=Sum('total_amount')).order_by('month')
        sales_values = [d['total_sales'] for d in data_sales]
        sales_values = [float(i) for i in sales_values]

        # Forecasted sales for next month
        last_month = data_sales[len(data_sales) - 1]['month']
        next_month = last_month + pd.DateOffset(months=1)
        next_month_label = next_month.strftime('%B %Y')
        data_df = pd.DataFrame({'sales': sales_values}, index=pd.to_datetime(labels, format='%B %Y'))
        data_df = data_df.asfreq('MS')
        fit = ExponentialSmoothing(data_df).fit()
        forecast = fit.forecast(1)
        next_month_sales = forecast[0]
        next_month_sales = float(next_month_sales)
        # round it to 1 decimal
        next_month_sales = round(next_month_sales, 1)
        sales_values.append(next_month_sales)

        # Forecasted profit for next month
        last_month = data_profit[len(data_profit) - 1]['month']
        next_month = last_month + pd.DateOffset(months=1)
        next_month_label = next_month.strftime('%B %Y')
        data_df = pd.DataFrame({'profit': profit_values}, index=pd.to_datetime(labels, format='%B %Y'))
        data_df = data_df.asfreq('MS')
        fit = ExponentialSmoothing(data_df).fit()
        forecast = fit.forecast(1)
        next_month_revenue = forecast[0]
        # convert to float
        next_month_revenue = float(next_month_revenue)
        # round it to 1 decimal
        next_month_revenue = round(next_month_revenue, 1)
        profit_values.append(next_month_revenue)

        # Add forecasted revenue label to labels list
        labels.append(next_month_label + ' (Forecasted)')

        # list year for filter
        list_year = []
        for order in Orders.objects.all():
            list_year.append(order.order_date.year)
        list_year = list(set(list_year))
        list_year.sort(reverse=True)

        # list month for filter
        list_month = []
        for order in Orders.objects.all():
            list_month.append(order.order_date.month)
        list_month = list(set(list_month))
        list_month.sort(reverse=True)

        if year != '':
            year = int(year)
        if month != '':
            month = int(month)

        context = {
            'sales': sales,
            'profit': profit,
            'view_count': view_count,
            'quality_product_sale': quality_product_sale,
            'product_sold_count': product_sold_count,
            'number_customer': number_customer,
            'payments': payments,
            'total_customers': total_customers,
            'total_orders': total_orders,
            'total_products': total_products,
            'total_discounts': total_discounts,
            'total_profit_ratio': total_profit_ratio,
            'total_feedback': total_feedback,
            'total_review': total_review,
            'total_payment': total_payment,
            'total_review_rate': total_review_rate,
            'orders': orders,
            'labels': labels,
            'profit_values': profit_values,
            'sales_values': sales_values,
            'top_10_best_selling_products': top_10_best_selling_products,
            'top_10_profitable_products': top_10_profitable_products,
            'top_10_most_viewed_products': top_10_most_viewed_products,
            'top_10_rated_products': top_10_rated_products,
            'list_year': list_year,
            'list_month': list_month,
            'year_selected': year,
            'month_selected': month,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
        }
        return render(request, 'dashboard/sales_statistics/sales_statistics.html', context)
