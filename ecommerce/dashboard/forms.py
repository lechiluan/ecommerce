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

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        if User.objects.filter(username=username).exists():
            self.add_error('username', 'Username already exists')
        if User.objects.filter(email=email).exists():
            self.add_error('email', 'Email already exists')


class UpdateCustomerForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    username = forms.CharField(required=True, max_length=20)
    email = forms.EmailField(required=True)
    address = forms.CharField(max_length=40, required=True)
    mobile = forms.CharField(validators=[phone_regex], max_length=20, required=True)
    is_active = forms.BooleanField(required=False, label='Active', initial=True)
    is_staff = forms.BooleanField(required=False, label='Staff', initial=False)
    is_superuser = forms.BooleanField(required=False, label='Superuser', initial=False)
    last_login_date = forms.CharField(required=False, label='Last Login',
                                      widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    date_joined_date = forms.CharField(required=False, label='Date Joined',
                                       widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'address', 'mobile',
                  'is_active', 'is_staff', 'is_superuser', 'date_joined_date', 'last_login_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            if self.instance.date_joined:
                self.fields['date_joined_date'].initial = self.instance.date_joined.strftime('%d/%m/%Y %I:%M:%S %p')
            if self.instance.last_login:
                self.fields['last_login_date'].initial = self.instance.last_login.strftime('%d/%m/%Y %I:%M:%S %p')

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            self.add_error('username', 'Username already exists')
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            self.add_error('email', 'Email already exists')

