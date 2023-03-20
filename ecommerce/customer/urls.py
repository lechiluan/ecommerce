from django.urls import path
from . import views

urlpatterns = [
    path('contact/', views.contact, name='contact'),
    path('cart/', views.cart, name='cart'),
    path('product_details/<int:product_id>/', views.product_details, name='product_details'),
]
