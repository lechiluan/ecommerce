from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

phone_regex = RegexValidator(regex=r'^(0|\+)\d{9,19}$', message="Phone number is invalid")


class AddCustomerForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField()
    address = forms.CharField(max_length=40, required=True)
    mobile = forms.CharField(validators=[phone_regex], max_length=20, required=True)
    is_active = forms.BooleanField(required=False, label='Active', initial=True)
    is_staff = forms.BooleanField(required=False, label='Staff', initial=False)
    is_superuser = forms.BooleanField(required=False, label='Superuser', initial=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2", "address", "mobile",
                  "is_active", "is_staff", "is_superuser"]


class UpdateCustomerForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    username = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    address = forms.CharField(max_length=40, required=True)
    mobile = forms.CharField(validators=[phone_regex], max_length=20, required=True)
    is_active = forms.BooleanField(required=False, label='Active', initial=True)
    is_staff = forms.BooleanField(required=False, label='Staff', initial=False)
    is_superuser = forms.BooleanField(required=False, label='Superuser', initial=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'address', 'mobile',
                  'is_active', 'is_staff', 'is_superuser']

