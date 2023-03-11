# from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from main.models import Customer
from django.contrib import messages
from .forms import AddCustomerForm, UpdateCustomerForm


# Create your views here.
def is_admin(user):
    return user.is_authenticated and user.is_superuser and user.is_staff and user.is_active


# @user_passes_test(is_admin, login_url='/auth/login/')
# # check if user is admin and if not redirect to login page after login successful it render page user request
# @login_required()
def admin_home(request):
    return render(request, 'dashboard/base/ad_base.html')


def user_customer_table(request):
    users = User.objects.all()
    customers = Customer.objects.all()
    return render(request, 'dashboard/customer-management/customer_table.html',
                  {'users': users, 'customers': customers})


def add_customer(request):
    if request.method == 'POST':
        form = AddCustomerForm(request.POST)
        if form.is_valid():
            form.save()
            customer = Customer.objects.create(user=User.objects.get(username=form.cleaned_data['username']),
                                               address=form.cleaned_data['address'],
                                               mobile=form.cleaned_data['mobile'])
            Customer.save(customer)
            messages.success(request, 'Customer added successfully!')

            if 'save_and_add' in request.POST:
                return redirect('/dashboard/add_customer/')
            elif 'save_and_update' in request.POST:
                return redirect('/dashboard/update_customer/' + str(customer.user.id))
            else:
                return redirect('/dashboard/customer_table/')

    else:
        form = AddCustomerForm()
    return render(request, 'dashboard/customer-management/add_customer.html', {'form': form})


def update_customer(request, user_id):
    user = User.objects.get(id=user_id)
    customer = Customer.objects.get(user_id=user_id)
    if request.method == 'POST':
        form = UpdateCustomerForm(request.POST, instance=user, initial={'mobile': customer.mobile,
                                                                        'address': customer.address})
        if form.is_valid():
            form.save()
            customer = Customer.objects.get(user=user)
            customer.address = form.cleaned_data['address']
            customer.mobile = form.cleaned_data['mobile']
            customer.save()
            messages.success(request, 'Customer updated successfully!')
            if 'save_and_add' in request.POST:
                return redirect('/dashboard/add_customer/')
            elif 'save_and_update' in request.POST:
                return redirect('dashboard/update_customer/' + str(customer.user.id))
            else:
                return redirect('/dashboard/customer_table/')
    else:
        user = User.objects.get(id=user_id)
        form = UpdateCustomerForm(instance=user, initial={'mobile': customer.mobile,
                                                          'address': customer.address})
    return render(request, 'dashboard/customer-management/update_customer.html', {'form': form})


def delete_customer(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        customer = Customer.objects.get(user=user)
    except ObjectDoesNotExist:
        messages.warning(request, 'The customer-management you are trying to delete does not exist!')
        return redirect('/dashboard/customer_table/')

    if user.is_superuser:
        messages.warning(request, 'Admin can not be deleted!')
    else:
        user.delete()
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
    return redirect('/dashboard/customer_table/')


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
                        messages.warning(request, 'Admin can not be deleted!')
                        return redirect('/dashboard/customer_table/')
                    else:
                        customer = Customer.objects.get(user=user)
                        customer.delete()
                        user.delete()
                        messages.success(request, 'Customer deleted successfully!')
                except ObjectDoesNotExist:
                    messages.warning(request, f'The customer-management with ID {user_id} does not exist!')
            return redirect('/dashboard/customer_table/')
        else:
            messages.warning(request, 'Please select at least one customer-management to delete!')
    return redirect('/dashboard/customer_table/')


def customer_details(request, user_id):
    user = User.objects.get(id=user_id)
    customer = Customer.objects.get(user_id=user_id)
    return render(request, 'dashboard/customer-management/customer_details.html',
                  {'user': user, 'customer': customer})


def search_customer(request):
    if request.method == 'POST':
        search_query = request.POST.get('search', '')
        customers = Customer.objects.filter(user__username__icontains=search_query) | Customer.objects.filter(
            user__email__icontains=search_query) | Customer.objects.filter(
            user__first_name__icontains=search_query) | Customer.objects.filter(
            user__last_name__icontains=search_query) | Customer.objects.filter(
            mobile__icontains=search_query) | Customer.objects.filter(
            address__icontains=search_query)
        users = [customer.user for customer in customers]
        if not users:
            messages.success(request, 'No customer-management found!')
            return redirect('/dashboard/customer_table/')
    else:
        users = User.objects.all()
        customers = Customer.objects.all()
    context = {'users': users, 'customers': customers}
    return render(request, 'dashboard/customer-management/customer_table.html', context)
