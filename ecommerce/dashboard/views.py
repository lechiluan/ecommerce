import os
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash, logout as auth_logout
from django.contrib.sites.shortcuts import get_current_site
from .forms import UpdateProfileForm, ChangePasswordForm, ChangeEmailForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
# Password Reset Imports
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
# from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from main.tokens import account_activation_token, password_reset_token, update_email_token
from django.contrib.auth.models import User
from django.conf import settings
from main.views import auth_login
from .forms import AddCustomerForm, UpdateCustomerForm, UpdateCustomerPasswordForm, AddCategoryForm, \
    UpdateCategoryForm, AddBrandForm, UpdateBrandForm, AddProductForm, UpdateProductForm, ChangeEmailForm
from main.models import Customer, Category, Brand, Product


# Create your views here.
def is_admin(user):
    return user.is_authenticated and user.is_superuser and user.is_staff and user.is_active


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def admin_home(request):
    return render(request, 'dashboard/base/ad_base.html')


# Administration Account
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
                    return render(request, 'dashboard/account/verify_new_email_sent.html')
            else:
                form.add_error('current_password', 'Password is incorrect')
                return render(request, "dashboard/account/change_email.html", {"form": form})
    else:
        form = ChangeEmailForm(instance=request.user)
    return render(request, "dashboard/account/change_email.html", {"form": form})


def send_verify_new_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Update your account.'
    message = render_to_string('dashboard/account/verify_new_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': update_email_token.make_token(user),
        'protocol': 'http',
    })
    to_email = [user.email]
    form_email = 'LCL Shop <lclshop.dev@gmail.com>'
    email = EmailMessage(mail_subject, message, form_email, to_email)
    email.content_subtype = "html"
    email.send()


def activate_new_email(request, uidb64, token):
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
        return redirect('/dashboard/profile/')
    else:
        return render(request, 'dashboard/account/verify_new_email_invalid.html')


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
            customer.customer_image = form.cleaned_data['customer_image']

            customer.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('/dashboard/profile/')
    else:
        form = UpdateProfileForm(instance=user, initial={'address': customer.address,
                                                         'mobile': customer.mobile,
                                                         'customer_image': customer.customer_image})
    return render(request, 'dashboard/account/update_profile.html', {'form': form})


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
                return redirect('/change_password_done/')
            else:
                form.add_error('old_password', 'Wrong password. Please try again.')
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, 'dashboard/account/change_password.html', {'form': form})


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def change_password_done(request):
    auth_logout(request)
    return render(request, 'dashboard/account/change_password_done.html')


def logout(request):
    auth_logout(request)
    messages.success(request, "You have logged out. See you again. Administrator!")
    return redirect('/')


# Customer Management
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


def paginator(request, objects):
    # Set the number of items per page
    per_page = 3

    # Create a Paginator object with the customers queryset and the per_page value
    page = Paginator(objects, per_page)

    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page')

    # Get the current page object from the Paginator object
    page_obj = page.get_page(page_number)
    return page_obj


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
                return redirect('/dashboard/customer/update/' + str(customer.user.id) + '/')
            else:
                return redirect('/dashboard/customer/')
    else:
        form = AddCustomerForm()
    context = {'form': form}
    return render(request, 'dashboard/manage_customer/add_customer.html', context)


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
                return redirect('/dashboard/customer/update/' + str(customer.user.id) + '/')
            else:
                return redirect('/dashboard/customer/')
    else:
        user = User.objects.get(id=user_id)
        form = UpdateCustomerForm(instance=user, initial={'mobile': customer.mobile,
                                                          'address': customer.address,
                                                          'customer_image': customer.customer_image})
    context = {'form': form}
    return render(request, 'dashboard/manage_customer/update_customer.html', context)


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


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def customer_details(request, user_id):
    user = User.objects.get(id=user_id)
    customer = Customer.objects.get(user_id=user_id)
    context = {'user': user, 'customer': customer}
    return render(request, 'dashboard/manage_customer/customer_details.html', context)


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def search_customer(request):
    if request.method == 'POST':
        search_query = request.POST.get('search', '')
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
               'customers': customers}
    return render(request, 'dashboard/manage_customer/customer_table.html', context)


# Category Management
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def category_table(request):
    # Get all categories
    categories = Category.objects.all().order_by('id')
    page_object = paginator(request, categories)
    context = {'categories': page_object}
    return render(request, 'dashboard/manage_category/category_table.html', context)


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def add_category(request):
    if request.method == 'POST':
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category {} added successfully!'.format(form.cleaned_data['name']))
            if 'save_and_add' in request.POST:
                return redirect('/dashboard/category/add/')
            elif 'save_and_update' in request.POST:
                return redirect('/dashboard/category/update' + str(form.cleaned_data['id']) + '/')
            else:
                return redirect('/dashboard/category/')
    else:
        form = AddCategoryForm()
    context = {'form': form}
    return render(request, 'dashboard/manage_category/add_category.html', context)


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


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def category_details(request, category_id):
    category = Category.objects.get(id=category_id)
    context = {'category': category}
    return render(request, 'dashboard/manage_category/category_details.html', context)


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def search_category(request):
    if request.method == 'POST':
        search_query = request.POST.get('search', '')
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
    context = {'categories': page_object}
    return render(request, 'dashboard/manage_category/category_table.html', context)


# Brand Management
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def brand_table(request):
    # Get all brands
    brands = Brand.objects.all().order_by('id')
    page_object = paginator(request, brands)
    context = {'brands': page_object}
    return render(request, 'dashboard/manage_brand/brand_table.html', context)


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def add_brand(request):
    if request.method == 'POST':
        form = AddBrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand {} added successfully!'.format(form.cleaned_data['name']))
            if 'save_and_add' in request.POST:
                return redirect('/dashboard/brand/add/')
            elif 'save_and_update' in request.POST:
                return redirect('/dashboard/brand/update/' + str(form.cleaned_data['id']) + '/')
            else:
                return redirect('/dashboard/brand/')
    else:
        form = AddBrandForm()
    context = {'form': form}
    return render(request, 'dashboard/manage_brand/add_brand.html', context)


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


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def brand_details(request, brand_id):
    brand = Brand.objects.get(id=brand_id)
    context = {'brand': brand}
    return render(request, 'dashboard/manage_brand/brand_details.html', context)


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def search_brand(request):
    if request.method == 'POST':
        search_query = request.POST.get('search', '')
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
    context = {'brands': page_object}
    return render(request, 'dashboard/manage_brand/brand_table.html', context)


# Product Management
@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def product_table(request):
    # Get all products
    products = Product.objects.all().order_by('id')
    page_object = paginator(request, products)
    context = {'products': page_object}
    return render(request, 'dashboard/manage_product/product_table.html', context)


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def add_product(request):
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product {} added successfully!'.format(form.cleaned_data['name']))
            if 'save_and_add' in request.POST:
                return redirect('/dashboard/product/add/')
            elif 'save_and_update' in request.POST:
                return redirect('/dashboard/product/update/' + str(form.cleaned_data['id']) + '/')
            else:
                return redirect('/dashboard/product/')
    else:
        form = AddProductForm()
    context = {'form': form}
    return render(request, 'dashboard/manage_product/add_product.html', context)


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


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def product_details(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {'product': product}
    return render(request, 'dashboard/manage_product/product_details.html', context)


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def search_product(request):
    if request.method == 'POST':
        search_query = request.POST.get('search', '')
        if search_query == '':
            messages.warning(request, 'Please enter a search term!')
            return redirect('/dashboard/product/')
        else:
            products = Product.objects.filter(name__icontains=search_query) | Product.objects.filter(
                description__icontains=search_query)
            page_object = paginator(request, products)
        if not products:
            messages.success(request, 'No products found {} !'.format(search_query))
    else:
        products = Product.objects.all()
        page_object = paginator(request, products)
    context = {'products': page_object}
    return render(request, 'dashboard/manage_product/product_table.html', context)
