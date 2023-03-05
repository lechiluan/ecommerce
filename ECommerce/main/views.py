from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash, logout as auth_logout
from django.contrib.sites.shortcuts import get_current_site

# from django.http import HttpResponse, HttpResponseRedirect
from .forms import RegisterForm, LoginForm, UpdateProfileForm, ChangePasswordForm, ChangeEmailForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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


# Create your views here.
def home(request):
    return render(request, 'main/base/base.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            if User.objects.filter(email=form.cleaned_data['email']).exists():
                form.add_error('email', 'Email is already exist. Please use another email.')
                return render(request, "registration/register/register.html", {"form": form})
            # check username is already exist
            elif User.objects.filter(username=form.cleaned_data['username']).exists():
                form.add_error('username', 'Username is already exist')
                return render(request, "registration/register/register.html", {"form": form})
            else:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                send_email_activate_account(request, user)
                return render(request, 'registration/register/account_activation_sent.html')
    else:
        form = RegisterForm()
    return render(request, 'registration/register/register.html', {'form': form})


def send_email_activate_account(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account.'
    message = render_to_string('registration/register/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'http',
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
            # check username and password is correct and authenticate

            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                # authenticate the user and log them in
                auth_login(request, user)
                # check if admin redirect to admin page else redirect to user page
                if form.cleaned_data['username'] == 'admin':
                    return redirect("/dashboard/home")
                else:
                    return redirect("/")
            else:
                username = form.cleaned_data['username']
                user = User.objects.filter(username=username).first()
                if user is not None and user.is_active is False:
                    send_email_activate_account(request, user)
                    messages.success(request, 'Your account is not active. Please check your email to '
                                              'activate your account.')
                    return render(request, "registration/login.html", {"form": form})
                form.add_error('username', 'Username or password is incorrect')
                return render(request, "registration/login.html", {"form": form})
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})


def send_verify_new_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Update your account.'
    message = render_to_string('registration/profile/verify_new_email.html', {
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
        return redirect('/profile/')
    else:
        return render(request, 'registration/register/account_activation_invalid.html')


@login_required
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            user = authenticate(username=request.user.username, password=form.cleaned_data['current_password'])
            if user is not None:
                # check if new email is already exist
                new_email = form.cleaned_data['new_email']
                if User.objects.filter(email=new_email).exists():
                    form.add_error('new_email', 'Email is already exist. Please enter another email.')
                    return render(request, "registration/profile/change_email.html", {"form": form})
                else:
                    user.email = form.cleaned_data['new_email']
                    user.is_active = False
                    user.save()
                    send_verify_new_email(request, user)
                    return render(request, 'registration/profile/verify_new_email_sent.html')
            else:
                form.add_error('password', 'Password is incorrect')
                return render(request, "registration/profile/change_email.html", {"form": form})
    else:
        form = ChangeEmailForm(instance=request.user)
    return render(request, "registration/profile/change_email.html", {"form": form})


@login_required
def update_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('/profile/')
    else:
        form = UpdateProfileForm(instance=user)
    return render(request, 'registration/profile/update_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = authenticate(username=request.user.username, password=form.cleaned_data['old_password'])
            if user is not None:
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                update_session_auth_hash(request, user)
                return redirect('change_password_done')
            else:
                form.add_error('old_password', 'Wrong password. Please try again.')
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, 'registration/profile/change_password.html', {'form': form})


@login_required
def change_password_done(request):
    auth_logout(request)
    return render(request, 'registration/profile/change_password_done.html')


def logout(request):
    auth_logout(request)
    return redirect('/')


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
                    site = get_current_site(request)
                    c = {
                        "email": user.email,
                        'domain': site,
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': password_reset_token.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    form_email = 'LCL Shop <lclshop.dev@gmail.com>'
                    # sender_email = settings.EMAIL_HOST_USER
                    try:
                        send_mail(subject, email, form_email, [user.email], fail_silently=False, html_message=email)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')

                return redirect("/password_reset/done/")
            else:
                password_reset_form.add_error('email', 'The email address entered does not exist in our database.')
                return render(request=request, template_name="registration/password/password_reset.html",
                              context={"password_reset_form": password_reset_form})
    else:
        password_reset_form = PasswordResetForm()
    return render(request=request, template_name="registration/password/password_reset.html",
                  context={"password_reset_form": password_reset_form})
