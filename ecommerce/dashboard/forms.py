from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from main.models import Category, Brand
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

phone_regex = RegexValidator(regex=r'^(0|\+)\d{9,19}$', message="Phone number is invalid")


def validate_image_size(value):
    filesize = value.size
    max_size = 2 * 1024 * 1024
    if filesize > max_size:
        raise ValidationError(_('Image size too large. Maximum size allowed is 2 MB.'))


# Customer Forms
class AddCustomerForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField()
    address = forms.CharField(max_length=40, required=True)
    mobile = forms.CharField(validators=[phone_regex], max_length=20, required=True)
    customer_image = forms.ImageField(required=False, label='Upload avatar')
    is_active = forms.BooleanField(required=False, label='Active', initial=True)
    is_staff = forms.BooleanField(required=False, label='Staff', initial=False)
    is_superuser = forms.BooleanField(required=False, label='Superuser', initial=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2", "address", "mobile",
                  "customer_image", "is_active", "is_staff", "is_superuser"]

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


class UpdateCustomerForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    username = forms.CharField(required=True, max_length=20)
    email = forms.EmailField(required=True)
    address = forms.CharField(max_length=40, required=True)
    mobile = forms.CharField(validators=[phone_regex], max_length=20, required=True)
    customer_image = forms.ImageField(required=False, label='Upload avatar')
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
        customer_image = cleaned_data.get('customer_image')
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            self.add_error('username', 'Username already exists')
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            self.add_error('email', 'Email already exists')
        if customer_image:
            validate_image_size(customer_image)


class UpdateCustomerPasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput, required=True, label='New Password')
    password2 = forms.CharField(widget=forms.PasswordInput, required=True, label='Confirm Password')

    class Meta:
        model = User
        fields = ['password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            self.add_error('password2', 'Passwords do not match')

    def save(self, user):
        password = self.cleaned_data.get('password1')
        user.set_password(password)
        user.save()
        return user


# Category Forms
class AddCategoryForm(forms.Form):
    name = forms.CharField(required=True, max_length=40)
    description = forms.CharField(required=True, max_length=100)

    class Meta:
        model = Category
        fields = ['name', 'description']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        if Category.objects.filter(name=name).exists():
            self.add_error('name', 'Category already exists')

    def save(self):
        name = self.cleaned_data.get('name')
        description = self.cleaned_data.get('description')
        category = Category(name=name, description=description)
        category.save()
        return category


class UpdateCategoryForm(forms.Form):
    name = forms.CharField(required=True, max_length=40)
    description = forms.CharField(required=True, max_length=100)

    class Meta:
        model = Category
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop('category')
        super().__init__(*args, **kwargs)

        if self.category:
            self.fields['name'].initial = self.category.name
            self.fields['description'].initial = self.category.description

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        if Category.objects.filter(name=name).exclude(id=self.category.id).exists():
            self.add_error('name', 'Category already exists')

    def save(self):
        name = self.cleaned_data.get('name')
        description = self.cleaned_data.get('description')
        self.category.name = name
        self.category.description = description
        self.category.save()
        return self.category


class AddBrandForm(forms.Form):
    name = forms.CharField(required=True, max_length=40)
    logo = forms.ImageField(required=True, label='Upload logo')

    class Meta:
        model = Brand
        fields = ['name', 'logo']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        logo = cleaned_data.get('logo')
        if Brand.objects.filter(name=name).exists():
            self.add_error('name', 'Brand already exists')
        if logo:
            validate_image_size(logo)

    def save(self):
        name = self.cleaned_data.get('name')
        logo = self.cleaned_data.get('logo')
        brand = Brand(name=name, logo=logo)
        brand.save()
        return brand


class UpdateBrandForm(forms.Form):
    name = forms.CharField(required=True, max_length=40)
    logo = forms.ImageField(required=False, label='Upload logo')

    class Meta:
        model = Brand
        fields = ['name', 'logo']

    def __init__(self, *args, **kwargs):
        self.brand = kwargs.pop('brand')
        super().__init__(*args, **kwargs)

        if self.brand:
            self.fields['name'].initial = self.brand.name
            self.fields['logo'].initial = self.brand.logo

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        logo = cleaned_data.get('logo')
        if Brand.objects.filter(name=name).exclude(id=self.brand.id).exists():
            self.add_error('name', 'Brand already exists')
        if logo:
            validate_image_size(logo)

    def save(self):
        name = self.cleaned_data.get('name')
        logo = self.cleaned_data.get('logo')
        self.brand.name = name
        self.brand.logo = logo
        self.brand.save()
        return self.brand
