# from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib import messages
import os
from django.conf import settings
from main.views import auth_login
from .forms import AddCustomerForm, UpdateCustomerForm, UpdateCustomerPasswordForm, AddCategoryForm, \
    UpdateCategoryForm, AddBrandForm, UpdateBrandForm
from main.models import Customer, Category, Brand


# Create your views here.
def is_admin(user):
    return user.is_authenticated and user.is_superuser and user.is_staff and user.is_active


@user_passes_test(is_admin, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def admin_home(request):
    return render(request, 'dashboard/base/ad_base.html')


# Customer Management
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


def customer_details(request, user_id):
    user = User.objects.get(id=user_id)
    customer = Customer.objects.get(user_id=user_id)
    context = {'user': user, 'customer': customer}
    return render(request, 'dashboard/manage_customer/customer_details.html', context)


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
def category_table(request):
    # Get all categories
    categories = Category.objects.all().order_by('id')
    page_object = paginator(request, categories)
    context = {'categories': page_object}
    return render(request, 'dashboard/manage_category/category_table.html', context)


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


def delete_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except ObjectDoesNotExist:
        messages.warning(request, 'The category {} you are trying to delete does not exist!'.format(category_id))
        return redirect('/dashboard/category/')

    category.delete()
    messages.success(request, 'Category {} deleted successfully!'.format(category.name))
    return redirect('/dashboard/category/')


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


def category_details(request, category_id):
    category = Category.objects.get(id=category_id)
    context = {'category': category}
    return render(request, 'dashboard/manage_category/category_details.html', context)


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
def brand_table(request):
    # Get all brands
    brands = Brand.objects.all().order_by('id')
    page_object = paginator(request, brands)
    context = {'brands': page_object}
    return render(request, 'dashboard/manage_brand/brand_table.html', context)


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


def delete_brand(request, brand_id):
    try:
        brand = Brand.objects.get(id=brand_id)
    except ObjectDoesNotExist:
        messages.warning(request, 'The brand {} you are trying to delete does not exist!'.format(brand_id))
        return redirect('/dashboard/brand/')
    brand.delete()
    messages.success(request, 'Brand {} deleted successfully!'.format(brand.name))


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


def brand_details(request, brand_id):
    brand = Brand.objects.get(id=brand_id)
    context = {'brand': brand}
    return render(request, 'dashboard/manage_brand/brand_details.html', context)


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
