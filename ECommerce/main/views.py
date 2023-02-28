from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash, logout as auth_logout
# from django.http import HttpResponse, HttpResponseRedirect
from .forms import RegisterForm, LoginForm, UpdateProfileForm, ChangePasswordForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test, login_required

# from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm


def is_admin(user):
    return user.is_authenticated and user.username == 'admin'


@user_passes_test(is_admin)
def admin_home(request):
    return render(request, 'dashboard/base/ad_base.html')


# Create your views here.
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
        form = LoginForm()
    return render(response, "registration/login.html", {"form": form})


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/profile')
    else:
        form = UpdateProfileForm(instance=request.user)
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
    return render(request, 'registration/change_password.html', {'form': form})


@login_required
def change_password_done(request):
    auth_logout(request)
    return render(request, 'registration/change_password_done.html')


def logout(request):
    auth_logout(request)
    return redirect('/')
