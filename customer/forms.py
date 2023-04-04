from django import forms
from django.core.validators import RegexValidator
from main.models import Category, Brand, Product, Coupon, Feedback, DeliveryAddress, Payment, Orders, OrderDetails
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

phone_regex = RegexValidator(regex=r'^(0|\+)\d{9,19}$', message="Phone number is invalid")


# Feedback Form
class FeedbackForm(forms.Form):
    name = forms.CharField(required=True, max_length=40, widget=forms.TextInput(attrs={'autofocus': True}))
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
