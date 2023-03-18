import datetime
from django import forms
from django.core.validators import RegexValidator
from main.models import Category, Brand, Product, Coupon, Contact
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

phone_regex = RegexValidator(regex=r'^(0|\+)\d{9,19}$', message="Phone number is invalid")


# Contact Form
class ContactForm(forms.Form):
    name = forms.CharField(required=True, max_length=100)
    email = forms.EmailField(required=True, max_length=100)
    mobile = forms.CharField(validators=[phone_regex], max_length=20, required=True)
    subject = forms.CharField(required=True, max_length=100)
    message = forms.CharField(required=True, max_length=2000, widget=forms.Textarea)

    class Meta:
        model = Contact
        fields = ['name', 'email', 'mobile', 'subject', 'message']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        mobile = cleaned_data.get('mobile')
        subject = cleaned_data.get('subject')
        message = cleaned_data.get('message')
        #  check a day just sent max 3 messages
        if Contact.objects.filter(email=email, created_at__date=datetime.date.today()).count() >= 3:
            self.add_error('email', 'You can only send 3 messages per day')
        if Contact.objects.filter(mobile=mobile, created_at__date=datetime.date.today()).count() >= 3:
            self.add_error('mobile', 'You can only send 3 messages per day')

    def save(self):
        name = self.cleaned_data.get('name')
        email = self.cleaned_data.get('email')
        mobile = self.cleaned_data.get('mobile')
        subject = self.cleaned_data.get('subject')
        message = self.cleaned_data.get('message')
        contact = Contact(name=name, email=email, mobile=mobile, subject=subject, message=message)
        contact.save()
        return contact


