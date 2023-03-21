import os
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash, logout as auth_logout
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
# Password Reset Imports
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
# from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from main.tokens import account_activation_token, password_reset_token, update_email_token
from django.contrib.auth.models import User
from django.conf import settings
from main.views import auth_login
from .forms import ContactForm
from main.models import Customer, Category, Brand, Product, Coupon, Contact


# Create your views here.
def cart(request):
    return render(request, 'customer_cart/cart.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'customer_help/contact.html', {'form': form})


def product_details(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {
        'product': product,
    }
    return render(request, 'customer_help/customer_product_details.html', context)
