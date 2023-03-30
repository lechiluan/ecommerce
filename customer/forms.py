import datetime
from django import forms
from django.core.validators import RegexValidator
from main.models import Category, Brand, Product, Coupon, Feedback, DeliveryAddress, Payment, Orders, OrderDetails
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

phone_regex = RegexValidator(regex=r'^(0|\+)\d{9,19}$', message="Phone number is invalid")


# Feedback Form
class FeedbackForm(forms.Form):
    name = forms.CharField(required=True, max_length=40)
    email = forms.EmailField(required=True, max_length=50)
    mobile = forms.CharField(validators=[phone_regex], max_length=20, required=True)
    subject = forms.CharField(required=True, max_length=100)
    message = forms.CharField(required=True, max_length=2000, widget=forms.Textarea)

    class Meta:
        model = Feedback
        fields = ['name', 'email', 'mobile', 'subject', 'message']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        mobile = cleaned_data.get('mobile')
        subject = cleaned_data.get('subject')
        message = cleaned_data.get('message')

        if not name:
            raise ValidationError(_('Please enter your name'))
        if not email:
            raise ValidationError(_('Please enter your email'))
        if not mobile:
            raise ValidationError(_('Please enter your mobile number'))
        if not subject:
            raise ValidationError(_('Please enter your subject'))
        if not message:
            raise ValidationError(_('Please enter your message'))

        return cleaned_data

    def save(self):
        feedback = Feedback(
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'],
            mobile=self.cleaned_data['mobile'],
            subject=self.cleaned_data['subject'],
            message=self.cleaned_data['message'],
        )
        feedback.save()
        return feedback


# Checkout Form
class CheckoutForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}), required=True,
                                 max_length=40)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}), required=True,
                                max_length=40)
    mobile = forms.CharField(max_length=20, validators=[phone_regex], required=True,
                             widget=forms.TextInput(attrs={'placeholder': 'Mobile'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}), required=True, max_length=50)
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address'}), required=True, max_length=500)
    city = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'City'}), required=True, max_length=40)
    state = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'State'}), required=True, max_length=40)
    zip_code = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Zip Code'}), required=True, max_length=10)
    country = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Country'}), required=True, max_length=40)
    is_default = forms.BooleanField(required=False, label='Set as default address')

    class Meta:
        model = DeliveryAddress
        fields = ['first_name', 'last_name', 'mobile', 'email', 'address', 'city', 'state', 'zip_code', 'country',
                  'is_default']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        mobile = cleaned_data.get('mobile')
        is_default = cleaned_data.get('is_default')
        if DeliveryAddress.objects.filter(email=email).exists():
            self.add_error('email', 'Email already exists')
        if DeliveryAddress.objects.filter(mobile=mobile).exists():
            self.add_error('mobile', 'Mobile already exists')
        if is_default:
            if DeliveryAddress.objects.filter(is_default=True).exists():
                self.add_error('is_default', 'Default address already exists')
            else:
                self.cleaned_data['is_default'] = True
        return cleaned_data

    def save(self):
        delivery_address = DeliveryAddress(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            mobile=self.cleaned_data['mobile'],
            email=self.cleaned_data['email'],
            address=self.cleaned_data['address'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            zip_code=self.cleaned_data['zip_code'],
            country=self.cleaned_data['country'],
            is_default=self.cleaned_data['is_default'],
        )
        delivery_address.save()
        return delivery_address


class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ['first_name', 'last_name', 'mobile', 'email', 'address', 'city', 'state', 'zip_code', 'country',
                  'is_default']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        mobile = cleaned_data.get('mobile')
        is_default = cleaned_data.get('is_default')
        if DeliveryAddress.objects.filter(email=email).exists():
            self.add_error('email', 'Email already exists')
        if DeliveryAddress.objects.filter(mobile=mobile).exists():
            self.add_error('mobile', 'Mobile already exists')
        if is_default:
            if DeliveryAddress.objects.filter(is_default=True).exists():
                self.add_error('is_default', 'Default address already exists')
            else:
                self.cleaned_data['is_default'] = True
        return cleaned_data

    def save(self, **kwargs):
        delivery_address = DeliveryAddress(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            mobile=self.cleaned_data['mobile'],
            email=self.cleaned_data['email'],
            address=self.cleaned_data['address'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            zip_code=self.cleaned_data['zip_code'],
            country=self.cleaned_data['country'],
            is_default=self.cleaned_data['is_default'],
        )
        delivery_address.save()
        return delivery_address


class CheckoutForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}), required=True,
                                 max_length=40)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}), required=True,
                                max_length=40)
    mobile = forms.CharField(max_length=20, validators=[phone_regex], required=True,
                             widget=forms.TextInput(attrs={'placeholder': 'Mobile'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}), required=True, max_length=50)
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address'}), required=True, max_length=500)
    city = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'City'}), required=True, max_length=40)
    state = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'State'}), required=True, max_length=40)
    zip_code = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Zip Code'}), required=True, max_length=10)
    country = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Country'}), required=True, max_length=40)
    is_default = forms.BooleanField(required=False, label='Set as default address')

    class Meta:
        model = DeliveryAddress
        fields = ['first_name', 'last_name', 'mobile', 'email', 'address', 'city', 'state', 'zip_code', 'country',
                  'is_default']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        mobile = cleaned_data.get('mobile')
        is_default = cleaned_data.get('is_default')
        if DeliveryAddress.objects.filter(email=email).exists():
            self.add_error('email', 'Email already exists')
        if DeliveryAddress.objects.filter(mobile=mobile).exists():
            self.add_error('mobile', 'Mobile already exists')
        if is_default:
            if DeliveryAddress.objects.filter(is_default=True).exists():
                self.add_error('is_default', 'Default address already exists')
            else:
                self.cleaned_data['is_default'] = True
        return cleaned_data

    def save(self):
        delivery_address = DeliveryAddress(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            mobile=self.cleaned_data['mobile'],
            email=self.cleaned_data['email'],
            address=self.cleaned_data['address'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            zip_code=self.cleaned_data['zip_code'],
            country=self.cleaned_data['country'],
            is_default=self.cleaned_data['is_default'],
        )
        delivery_address.save()
        return delivery_address
