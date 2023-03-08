from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class RegisterForm(UserCreationForm):
    phone_regex = RegexValidator(regex=r'^(0|\+)\d{9,19}$', message="Phone number is invalid")
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField()
    address = forms.CharField(max_length=40, required=True)
    mobile = forms.CharField(validators=[phone_regex], max_length=20, required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2", "address", "mobile"]


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    rememberMe = forms.BooleanField(required=False, label='Remember me', initial=False)

    class Meta:
        model = User
        fields = ["username", "password"]


class UpdateProfileForm(forms.ModelForm):
    phone_regex = RegexValidator(regex=r'^(0|\+)\d{9,19}$', message="Phone number is invalid")
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    username = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    address = forms.CharField(max_length=40, required=True)
    mobile = forms.CharField(validators=[phone_regex], max_length=20, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'address', 'mobile']


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label='Old password', widget=forms.PasswordInput(
        attrs={'autocomplete': 'current-password', 'autofocus': True}))

    class Meta:
        fields = ['old_password', 'new_password1', 'new_password2']


class ChangeEmailForm(forms.ModelForm):
    email = forms.EmailField(label='Current Email', widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    current_password = forms.CharField(label='Current Password', widget=forms.PasswordInput())
    new_email = forms.EmailField(label='New Email')

    class Meta:
        model = User
        fields = ['email', 'new_email', 'current_password']
