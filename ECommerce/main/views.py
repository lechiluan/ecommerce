from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash, logout as auth_logout
# from django.http import HttpResponse, HttpResponseRedirect
from .forms import RegisterForm, LoginForm, UpdateProfileForm, ChangePasswordForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# Password Reset Imports
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes




def home(request):
    return render(request, 'main/base/base.html')


def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()
            return redirect("/login")
    else:
        form = RegisterForm()
    return render(response, "registration/register.html", {"form": form})


def login(response):
    if response.method == "POST":
        form = LoginForm(response.POST)
        if form.is_valid():
            # check username and password is correct and authenticate
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                # authenticate the user and log them in
                auth_login(response, user)

                # check if admin redirect to admin page else redirect to user page
                if form.cleaned_data['username'] == 'admin':
                    return redirect("/dashboard/home")
                else:
                    return redirect("/")
            else:
                # clean input username
                form.cleaned_data['username'] = ''
                form.cleaned_data['password'] = ''
                form.add_error('username', 'Username or password is incorrect')
    else:
        form = LoginForm()
    return render(response, "registration/login.html", {"form": form})


@login_required
def update_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('/profile')
    else:
        form = UpdateProfileForm(instance=user)
    return render(request, 'registration/update_profile.html', {'form': form})


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
    return render(request, 'registration/password/change_password.html', {'form': form})


@login_required
def change_password_done(request):
    auth_logout(request)
    return render(request, 'registration/password/change_password_done.html')


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
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
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
