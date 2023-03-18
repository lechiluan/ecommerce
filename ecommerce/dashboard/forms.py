from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from main.models import Category, Brand, Product, Coupon, Contact, Payment
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

phone_regex = RegexValidator(regex=r'^(0|\+)\d{9,19}$', message="Phone number is invalid")


def validate_image_size(value):
    filesize = value.size
    max_size = 2 * 1024 * 1024
    if filesize > max_size:
        raise ValidationError(_('Image size too large. Maximum size allowed is 2 MB.'))


# Administrator Forms
class UpdateProfileForm(forms.ModelForm):
    phone_regex = RegexValidator(regex=r'^(0|\+)\d{9,19}$', message="Phone number is invalid")
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    username = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    address = forms.CharField(max_length=40, required=True)
    mobile = forms.CharField(validators=[phone_regex], max_length=20, required=True)
    customer_image = forms.ImageField(required=False, label='Upload avatar')

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
    customer_image = forms.ImageField(required=False, label='Upload new avatar', widget=forms.FileInput,
                                      help_text='(5MB max size)', error_messages={'invalid': 'Image files only'})
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
    logo = forms.ImageField(required=True, label='Upload logo', widget=forms.FileInput,
                            help_text='(5MB max size)', error_messages={'invalid': 'Image files only'})

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
    logo = forms.ImageField(required=True, label='Upload new logo', widget=forms.FileInput,
                            help_text='(5MB max size)', error_messages={'invalid': 'Image files only'})

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


# Product Forms
class AddProductForm(forms.Form):
    name = forms.CharField(required=True, max_length=40)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True, empty_label="Select Category")
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(), required=True, empty_label="Select Brand")
    price = forms.DecimalField(required=True, max_digits=10, decimal_places=2)
    old_price = forms.DecimalField(required=False, max_digits=10, decimal_places=2)
    stock = forms.IntegerField(required=True)
    description = forms.CharField(required=True, widget=forms.Textarea)
    product_image = forms.ImageField(required=True, label='Upload Product Image', widget=forms.FileInput,
                                     help_text='(5MB max size)', error_messages={'invalid': 'Image files only'})

    class Meta:
        model = Product
        fields = ['name', 'category', 'brand', 'price', 'old_price', 'stock', 'description', 'product_image']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        category = cleaned_data.get('category')
        brand = cleaned_data.get('brand')
        price = cleaned_data.get('price')
        old_price = cleaned_data.get('old_price')
        stock = cleaned_data.get('stock')
        description = cleaned_data.get('description')
        product_image = cleaned_data.get('product_image')
        if Product.objects.filter(name=name).exists():
            self.add_error('name', 'Product already exists')
        if product_image:
            validate_image_size(product_image)

    def save(self):
        name = self.cleaned_data.get('name')
        category = self.cleaned_data.get('category')
        brand = self.cleaned_data.get('brand')
        price = self.cleaned_data.get('price')
        old_price = self.cleaned_data.get('old_price')
        stock = self.cleaned_data.get('stock')
        description = self.cleaned_data.get('description')
        product_image = self.cleaned_data.get('product_image')
        product = Product(name=name, category=category, brand=brand, price=price, old_price=old_price, stock=stock,
                          description=description, product_image=product_image)
        product.save()
        return product


class UpdateProductForm(forms.Form):
    name = forms.CharField(required=True, max_length=40)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True)
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(), required=True)
    price = forms.DecimalField(required=True, max_digits=10, decimal_places=2)
    old_price = forms.DecimalField(required=False, max_digits=10, decimal_places=2)
    stock = forms.IntegerField(required=True)
    description = forms.CharField(required=True, max_length=5000, widget=forms.Textarea)
    product_image = forms.ImageField(required=True, label='Upload New Product Image', widget=forms.FileInput,
                                     help_text='(5MB max size)', error_messages={'invalid': 'Image files only'})

    class Meta:
        model = Product
        fields = ['name', 'category', 'brand', 'price', 'old_price', 'stock', 'description', 'product_image']

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product')
        super().__init__(*args, **kwargs)

        if self.product:
            self.fields['name'].initial = self.product.name
            self.fields['category'].initial = self.product.category
            self.fields['brand'].initial = self.product.brand
            self.fields['price'].initial = self.product.price
            self.fields['old_price'].initial = self.product.old_price
            self.fields['stock'].initial = self.product.stock
            self.fields['description'].initial = self.product.description
            self.fields['product_image'].initial = self.product.product_image

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        category = cleaned_data.get('category')
        brand = cleaned_data.get('brand')
        price = cleaned_data.get('price')
        old_price = cleaned_data.get('old_price')
        stock = cleaned_data.get('stock')
        description = cleaned_data.get('description')
        product_image = cleaned_data.get('product_image')
        if Product.objects.filter(name=name).exclude(id=self.product.id).exists():
            self.add_error('name', 'Product already exists')
        if product_image:
            validate_image_size(product_image)

    def save(self):
        name = self.cleaned_data.get('name')
        category = self.cleaned_data.get('category')
        brand = self.cleaned_data.get('brand')
        price = self.cleaned_data.get('price')
        old_price = self.cleaned_data.get('old_price')
        stock = self.cleaned_data.get('stock')
        description = self.cleaned_data.get('description')
        product_image = self.cleaned_data.get('product_image')
        self.product.name = name
        self.product.category = category
        self.product.brand = brand
        self.product.price = price
        self.product.old_price = old_price
        self.product.stock = stock
        self.product.description = description
        if product_image:
            self.product.product_image = product_image
        self.product.save()
        return self.product


# Coupon Forms
class AddCouponForm(forms.Form):
    code = forms.CharField(required=True, max_length=20)
    discount = forms.DecimalField(required=True, max_digits=10, decimal_places=2)
    amount = forms.IntegerField(required=True, min_value=1)
    valid_from = forms.DateTimeField(required=True, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    valid_to = forms.DateTimeField(required=True, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    active = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Coupon
        fields = ['code', 'discount', 'amount', 'valid_from', 'valid_to', 'active']

    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get('code')
        discount = cleaned_data.get('discount')
        amount = cleaned_data.get('amount')
        valid_from = cleaned_data.get('valid_from')
        valid_to = cleaned_data.get('valid_to')
        active = cleaned_data.get('active')
        if Coupon.objects.filter(code=code).exists():
            self.add_error('code', 'Coupon already exists')
        if valid_from > valid_to:
            self.add_error('valid_from', 'Valid from date must be before valid to date')
        if valid_to < valid_from:
            self.add_error('valid_to', 'Valid to date must be after valid from date')

    def save(self):
        code = self.cleaned_data.get('code')
        discount = self.cleaned_data.get('discount')
        amount = self.cleaned_data.get('amount')
        valid_from = self.cleaned_data.get('valid_from')
        valid_to = self.cleaned_data.get('valid_to')
        active = self.cleaned_data.get('active')
        coupon = Coupon(code=code, discount=discount, amount=amount, valid_from=valid_from, valid_to=valid_to,
                        active=active)
        coupon.save()
        return coupon


class UpdateCouponForm(forms.Form):
    code = forms.CharField(required=True, max_length=20)
    discount = forms.DecimalField(required=True, max_digits=10, decimal_places=2)
    amount = forms.IntegerField(required=True, min_value=1)
    valid_from = forms.DateTimeField(required=True, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    valid_to = forms.DateTimeField(required=True, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    active = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Coupon
        fields = ['code', 'discount', 'amount', 'valid_from', 'valid_to', 'active']

    def __init__(self, *args, **kwargs):
        self.coupon = kwargs.pop('coupon')
        super().__init__(*args, **kwargs)

        if self.coupon:
            self.fields['code'].initial = self.coupon.code
            self.fields['discount'].initial = self.coupon.discount
            self.fields['amount'].initial = self.coupon.amount
            self.fields['valid_from'].initial = self.coupon.valid_from
            self.fields['valid_to'].initial = self.coupon.valid_to
            self.fields['active'].initial = self.coupon.active

    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get('code')
        discount = cleaned_data.get('discount')
        amount = cleaned_data.get('amount')
        valid_from = cleaned_data.get('valid_from')
        valid_to = cleaned_data.get('valid_to')
        active = cleaned_data.get('active')
        if Coupon.objects.filter(code=code).exclude(id=self.coupon.id).exists():
            self.add_error('code', 'Coupon already exists')
        if valid_from > valid_to:
            self.add_error('valid_from', 'Valid from date must be before valid to date')
        if valid_to < valid_from:
            self.add_error('valid_to', 'Valid to date must be after valid from date')

    def save(self):
        code = self.cleaned_data.get('code')
        discount = self.cleaned_data.get('discount')
        amount = self.cleaned_data.get('amount')
        valid_from = self.cleaned_data.get('valid_from')
        valid_to = self.cleaned_data.get('valid_to')
        active = self.cleaned_data.get('active')
        self.coupon.code = code
        self.coupon.discount = discount
        self.coupon.amount = amount
        self.coupon.valid_from = valid_from
        self.coupon.valid_to = valid_to
        self.coupon.active = active
        self.coupon.save()
        return self.coupon


# Payment Forms
class AddPaymentForm(forms.Form):
    name = forms.CharField(required=True, max_length=20)
    active = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Payment
        fields = ['name', 'active']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        active = cleaned_data.get('active')
        if Payment.objects.filter(name=name).exists():
            self.add_error('name', 'Payment already exists')

    def save(self):
        name = self.cleaned_data.get('name')
        active = self.cleaned_data.get('active')
        payment = Payment(name=name, active=active)
        payment.save()
        return payment
