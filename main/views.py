from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash, logout as auth_logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Count, Avg

# from django.http import HttpResponse, HttpResponseRedirect
from .forms import RegisterForm, LoginForm, UpdateProfileForm, ChangePasswordForm, ChangeEmailForm, \
    AddDeliveryAddressForm, UpdateDeliveryAddressForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
# Password Reset Imports
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
# from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token, password_reset_token, update_email_token
from django.contrib.auth.models import User
from .models import Customer, Product, Category, Brand, DeliveryAddress, Review


# Create your views here.
def paginator(request, objects):
    # Set the number of items per page
    per_page = 8

    # Create a Paginator object with the customers queryset and the per_page value
    page = Paginator(objects, per_page)

    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page')

    # Get the current page object from the Paginator object
    page_obj = page.get_page(page_number)
    return page_obj


# Display Homepage for all users. Display List of all products, categories, brands, etc.
def home(request):
    products = Product.objects.all().order_by('-sold')
    categories = Category.objects.all().order_by('id')
    brands = Brand.objects.all().order_by('id')
    page_object = paginator(request, products)
    best_selling_products = Product.objects.all().order_by('-sold')[:4]
    recommended_products = Product.objects.all().order_by('-view_count')[:4]

    context = {'products': page_object,
               'categories': categories,
               'brands': brands,
               'best_selling_products': best_selling_products,
               'recommended_products': recommended_products
               }
    return render(request, 'main/base/base.html', context)


def is_admin(user):
    return user.is_authenticated and user.is_active and user.is_superuser and user.is_staff


def is_customer(user):
    return user.is_authenticated and user.is_active


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            if User.objects.filter(email=form.cleaned_data['email']).exists():
                form.add_error('email', 'Email is already exist. Please use another email.')
                return render(request, "registration/register/register.html", {"form": form})
            elif User.objects.filter(username=form.cleaned_data['username']).exists():
                form.add_error('username', 'Username is already exist')
                return render(request, "registration/register/register.html", {"form": form})
            else:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                customer = Customer.objects.create(user=user)
                customer.address = form.cleaned_data['address']
                customer.mobile = form.cleaned_data['mobile']
                customer.customer_image = form.cleaned_data['customer_image']
                customer.save()

                send_email_activate_account(request, user)
                return render(request, 'registration/register/account_activation_sent.html')
        else:
            if form.errors.get('captcha'):
                messages.warning(request, 'Please check the captcha to verify that you are not a robot')
            return render(request, "registration/register/register.html", {"form": form})
    else:
        form = RegisterForm()
    return render(request, 'registration/register/register.html', {'form': form})


def terms_and_conditions(request):
    return render(request, 'main/base/terms_and_conditions.html')


def privacy_policy(request):
    return render(request, 'main/base/privacy_policy.html')


def send_email_activate_account(request, user):
    protocol = 'http' if request.scheme == 'http' else 'https'
    current_site = get_current_site(request)
    mail_subject = 'Activate your account.'
    message = render_to_string('registration/register/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': protocol,
    })
    to_email = [user.email]
    form_email = 'LCL Shop <lclshop.dev@gmail.com>'
    email = EmailMessage(mail_subject, message, form_email, to_email)
    email.content_subtype = "html"
    email.send()


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        auth_login(request, user)
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('/')
    else:
        return render(request, 'registration/register/account_activation_invalid.html')


def login(request, *args, **kwargs):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                # authenticate the user and log them in
                auth_login(request, user)
                # check if admin redirect to admin page else redirect to user page
                if user.is_superuser and user.is_staff and user.is_active:
                    messages.success(request, 'Welcome back administrator!')
                    next_url = request.GET.get('next', '/dashboard/')
                    return redirect(next_url)
                else:
                    messages.success(request, 'Welcome back {}'.format(user.username))
                    next_url = request.GET.get('next', '/')
                    return redirect(next_url)
            else:
                username = form.cleaned_data['username']
                user = User.objects.filter(username=username).first()
                if user is not None and user.is_active is False:
                    send_email_activate_account(request, user)
                    messages.warning(request, 'Your account is not active. Please check your email {} to '
                                              'activate your account.'.format(user.email))
                    return render(request, "registration/login.html", {"form": form})
                form.add_error('username', 'Username or password is incorrect')
                return render(request, "registration/login.html", {"form": form})
        else:
            if form.errors.get('captcha'):
                messages.warning(request, 'Please check the captcha to verify that you are not a robot')
            return render(request, "registration/login.html", {"form": form})
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})


def send_verify_new_email(request, user):
    protocol = 'http' if request.scheme == 'http' else 'https'
    current_site = get_current_site(request)
    mail_subject = 'Update your account.'
    message = render_to_string('registration/profile/verify_new_email.html', {
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
        return redirect('/auth/change_email/')
    else:
        return render(request, 'registration/profile/verify_new_email_invalid.html')


@user_passes_test(is_customer, login_url='/auth/login/')
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
                    return render(request, "registration/profile/change_email.html", {"form": form})
                elif User.objects.filter(email=new_email).exists():
                    form.add_error('new_email', 'Email is already exist. Please enter another email.')
                    return render(request, "registration/profile/change_email.html", {"form": form})
                else:
                    user.email = form.cleaned_data['new_email']
                    user.is_active = False
                    user.save()
                    send_verify_new_email(request, user)
                    return render(request, 'registration/profile/verify_new_email_sent.html', {'email': user.email})
            else:
                form.add_error('current_password', 'Password is incorrect')
                return render(request, "registration/profile/change_email.html", {"form": form})
    else:
        form = ChangeEmailForm(instance=request.user)
    return render(request, "registration/profile/change_email.html", {"form": form})


@user_passes_test(is_customer, login_url='/auth/login/')
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
            return redirect('/auth/profile/')
    else:
        form = UpdateProfileForm(instance=user, initial={'address': customer.address,
                                                         'mobile': customer.mobile,
                                                         'customer_image': customer.customer_image})
    return render(request, 'registration/profile/update_profile.html', {'form': form})


@user_passes_test(is_customer, login_url='/auth/login/')
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
                return redirect('/auth/change_password/')
            else:
                form.add_error('old_password', 'Wrong password. Please try again.')
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, 'registration/profile/change_password.html', {'form': form})


def logout(request):
    auth_logout(request)
    # Clear Google Recaptcha session
    if 'google_recaptcha' in request.session:
        del request.session['google_recaptcha']
    messages.success(request, "You have logged out. See you again!")
    return redirect('/auth/login/')


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "registration/password/password_reset_email.html"
                    protocol = 'http' if request.scheme == 'http' else 'https'
                    site = get_current_site(request)
                    c = {
                        "email": user.email,
                        'domain': site,
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': password_reset_token.make_token(user),
                        'protocol': protocol,
                    }
                    email = render_to_string(email_template_name, c)
                    form_email = 'LCL Shop <lclshop.dev@gmail.com>'
                    # sender_email = settings.EMAIL_HOST_USER
                    try:
                        send_mail(subject, email, form_email, [user.email], fail_silently=False, html_message=email)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')

                return redirect("/auth/password_reset/done/")
            else:
                password_reset_form.add_error('email', 'The email address entered does not exist. Please try again')
                return render(request=request, template_name="registration/password/password_reset.html",
                              context={"password_reset_form": password_reset_form})
    else:
        password_reset_form = PasswordResetForm()
    return render(request=request, template_name="registration/password/password_reset.html",
                  context={"password_reset_form": password_reset_form})


# Delivery Address Management
# Delivery Address table
@login_required(login_url='/auth/login/')
def delivery_address_table(request):
    # Get all delivery addresses
    customer = Customer.objects.filter(user=request.user).first()
    delivery_addresses = DeliveryAddress.objects.filter(customer=customer).order_by('-id')
    page_object = paginator(request, delivery_addresses)
    context = {'delivery_addresses': page_object,
               'customer': customer}
    return render(request, 'registration/address/delivery_address_table.html', context)


@login_required(login_url='/auth/login/')
def add_delivery_address(request):
    customer = Customer.objects.filter(user=request.user).first()
    if request.method == 'POST':
        form = AddDeliveryAddressForm(customer=customer, data=request.POST)
        if form.is_valid():
            delivery_address = form.save(commit=False)
            delivery_address.customer = customer
            delivery_address.save()
            messages.success(request, 'Delivery address added successfully!')
            next_url = request.GET.get('next', '/auth/delivery_address/')
            return redirect(next_url)
    else:
        form = AddDeliveryAddressForm(customer=customer)
    context = {'form': form}
    return render(request, 'registration/address/add_delivery_address.html', context)


@login_required(login_url='/auth/login/')
def update_delivery_address(request, delivery_address_id):
    # Get the delivery address
    customer = Customer.objects.filter(user=request.user).first()
    delivery_address = DeliveryAddress.objects.get(id=delivery_address_id)
    if request.method == 'POST':
        form = UpdateDeliveryAddressForm(customer=customer, instance=delivery_address, data=request.POST)
        if form.is_valid():
            delivery_address = form.save(commit=False)
            delivery_address.customer = customer
            delivery_address.save()
            messages.success(request, 'Delivery address updated successfully!')
            next_url = request.GET.get('next', '/auth/delivery_address/')
            return redirect(next_url)
    else:
        form = UpdateDeliveryAddressForm(customer=customer, instance=delivery_address)
    context = {'form': form,
               'delivery_address': delivery_address}
    return render(request, 'registration/address/update_delivery_address.html', context)


# Delete delivery address
@login_required(login_url='/auth/login/')
def delete_delivery_address(request, delivery_address_id):
    try:
        delivery_address = DeliveryAddress.objects.get(id=delivery_address_id)
    except ObjectDoesNotExist:
        messages.warning(request,
                         'The delivery address {} you are trying to delete does not exist!'.format(delivery_address_id))
        return redirect('/auth/delivery_address/')
    if delivery_address.is_default:
        messages.warning(request, 'You cannot delete the default delivery address!')
        return redirect('/auth/delivery_address/')
    delivery_address.delete()
    messages.success(request, 'Delivery address {} deleted successfully!'.format(delivery_address_id))
    return redirect('/auth/delivery_address/')


# Delete selected delivery addresses
@login_required(login_url='/auth/login/')
def delete_selected_delivery_address(request, delivery_address_ids):
    if request.method == 'POST':
        # Get a list of delivery address IDs to delete
        delivery_address_ids = delivery_address_ids.split("+")
        # Delete the delivery addresses
        if delivery_address_ids:
            for delivery_address_id in delivery_address_ids:
                try:
                    delivery_address = DeliveryAddress.objects.get(id=delivery_address_id)
                    if delivery_address.is_default:
                        messages.warning(request, 'You cannot delete the default delivery address!')
                        return redirect('/auth/delivery_address/')
                    else:
                        delivery_address.delete()
                        messages.success(request, 'Delivery address deleted successfully!')
                except ObjectDoesNotExist:
                    messages.warning(request, f'The delivery address with ID {delivery_address_id} does not exist!')
            return redirect('/auth/delivery_address/')
        else:
            messages.warning(request, 'Please select at least one delivery address to delete!')
    return redirect('/auth/delivery_address/')


# Search delivery address
@login_required(login_url='/auth/login/')
def search_delivery_address(request):
    search_query = request.POST.get('search', '')
    if request.method == 'POST':
        if search_query == '':
            messages.warning(request, 'Please enter a search term!')
            return redirect('/auth/delivery_address/')
        else:
            delivery_addresses = DeliveryAddress.objects.filter(
                id__icontains=search_query) | DeliveryAddress.objects.filter(
                first_name__icontains=search_query) | DeliveryAddress.objects.filter(
                email__icontains=search_query) | DeliveryAddress.objects.filter(
                address__icontains=search_query) | DeliveryAddress.objects.filter(
                city__icontains=search_query) | DeliveryAddress.objects.filter(
                state__icontains=search_query) | DeliveryAddress.objects.filter(
                zip_code__icontains=search_query) | DeliveryAddress.objects.filter(
                mobile__icontains=search_query) | DeliveryAddress.objects.filter(
                date_added__icontains=search_query) | DeliveryAddress.objects.filter(
                last_name__icontains=search_query)
            page_object = paginator(request, delivery_addresses)
        if not delivery_addresses:
            messages.success(request, 'No delivery addresses found {} !'.format(search_query))
    else:
        delivery_addresses = DeliveryAddress.objects.all()
        page_object = paginator(request, delivery_addresses)
    context = {'delivery_addresses': page_object,
               'search_query': search_query}
    return render(request, 'registration/address/delivery_address_table.html', context)


@login_required(login_url='/auth/login/')
def set_default_delivery_address(request, delivery_address_id):
    # Get the delivery address
    delivery_address = DeliveryAddress.objects.get(id=delivery_address_id)
    if delivery_address.is_default:
        messages.warning(request, 'Delivery address is already set as default!')
        return redirect('/auth/delivery_address/')
    else:
        # Set all delivery addresses to not default
        DeliveryAddress.objects.all().update(is_default=False)
        # Set the selected delivery address to default
        delivery_address.is_default = True
        delivery_address.save()
        messages.success(request, 'Delivery address set as default successfully!')
        return redirect('/auth/delivery_address/')
