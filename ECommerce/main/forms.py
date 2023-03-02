from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator # for phone number validation


class RegisterForm(UserCreationForm):
    phone_regex = RegexValidator(regex=r'^\d{10,11}$', message="Phone number is invalid")
    email = forms.EmailField()
    phone = forms.CharField(validators=[phone_regex])
    address = forms.CharField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2", "phone", "address"]


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "password"]


class UpdateProfileForm(forms.ModelForm):
    phone_regex = RegexValidator(regex=r'^\d{10,11}$', message="Phone number is invalid")
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Phone'}), validators=[phone_regex])
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address']


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label='Old password', widget=forms.PasswordInput(
        attrs={'autocomplete': 'current-password', 'autofocus': True}))

    class Meta:
        fields = ['old_password', 'new_password1', 'new_password2']

