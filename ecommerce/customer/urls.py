from django.urls import path
from . import views

urlpatterns = [
    path('send_email_newsletter/', views.send_email_newsletter, name='send_email_newsletter'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('product/details/<int:product_id>/', views.product_details, name='product_details'),
    path('product/search/', views.product_search, name='search'),
    path('product/category/<int:category_id>/', views.product_list_category, name='product_list_category'),
    path('product/brand/<int:brand_id>/', views.product_list_brand, name='product_list_brand'),


    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.view_wishlist, name='wishlist'),
    # path('add_to_cart_from_wishlist/<int:wishlist_id>/', views.add_to_cart_from_wishlist,
    #      name='add_to_cart_from_wishlist'),
    path('add_all_to_cart_from_wishlist/', views.add_all_to_cart_form_wishlist, name='add_all_to_cart_from_wishlist'),


    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart/', views.update_cart_quantity, name='update_cart'),

    path('checkout/', views.checkout, name='checkout'),
]
