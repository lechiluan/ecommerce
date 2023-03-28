from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_image_size(value):
    filesize = value.size
    max_size = 2 * 1024 * 1024
    if filesize > max_size:
        raise ValidationError(_('Image size too large. Maximum size allowed is 2 MB.'))


class RegisterForm(UserCreationForm):
    phone_regex = RegexValidator(regex=r'^(0|\+)\d{9,19}$', message="Phone number is invalid")
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField()
    address = forms.CharField(max_length=40, required=True)
    mobile = forms.CharField(validators=[phone_regex], max_length=20, required=True)
    customer_image = forms.ImageField(required=False, label='Upload avatar', widget=forms.FileInput,
                                      help_text='(5MB max size)', error_messages={'invalid': 'Image files only'})
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2", "address", "mobile",
                  "customer_image"]

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        customer_image = cleaned_data.get('customer_image')

        if User.objects.filter(username=username).exists():
            self.add_error('username', 'Username already exists')
        if User.objects.filter(email=email).exists():
            self.add_error('email', 'Email already exists')
        if customer_image:
            validate_image_size(customer_image)


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
    customer_image = forms.ImageField(required=False, label='Upload new avatar', widget=forms.FileInput,
                                      help_text='(5MB max size)', error_messages={'invalid': 'Image files only'})

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'address', 'mobile', 'customer_image']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        customer_image = cleaned_data.get('customer_image')
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            self.add_error('username', 'Username already exists')
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            self.add_error('email', 'Email already exists')
        if customer_image:
            validate_image_size(customer_image)


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


    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        new_email = cleaned_data.get('new_email')
        current_password = cleaned_data.get('current_password')
        if User.objects.filter(email=new_email).exclude(id=self.instance.id).exists():
            self.add_error('new_email', 'Email already exists')
        if not self.instance.check_password(current_password):
            self.add_error('current_password', 'Password is incorrect')


