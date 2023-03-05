# from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test, login_required

# from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm


# Create your views here.
def is_admin(user):
    return user.is_authenticated and user.is_superuser and user.is_staff


# @user_passes_test(is_admin, login_url='/auth/login/')
# # check if user is admin and if not redirect to login page after login successful it render page user request
# @login_required()
def admin_home(request):
    return render(request, 'dashboard/base/ad_base.html')