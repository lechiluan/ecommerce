from django.urls import path
from . import views

urlpatterns = [
    path('send_email_newsletter/', views.send_email_newsletter, name='send_email_newsletter'),
    path('feedback/', views.send_feedback, name='contact'),
    path('about/', views.about, name='about'),
    path('product/details/<str:slug>/', views.product_details, name='product_details'),
    path('product/search/', views.product_search, name='search'),
    path('product/category/<str:slug>/', views.product_list_category, name='product_list_category'),
    path('product/brand/<str:slug>/', views.product_list_brand, name='product_list_brand'),
    path('product/add_review/<str:slug>/', views.add_review, name='add_review'),
    path('product/edit_review/<int:review_id>/', views.edit_review, name='edit_review'),
    path('product/delete_review/<int:review_id>/', views.delete_review, name='delete_review'),

    path('add_to_wishlist/<str:slug>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<str:slug>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.view_wishlist, name='wishlist'),
    # path('add_to_cart_from_wishlist/<int:wishlist_id>/', views.add_to_cart_from_wishlist,
    #      name='add_to_cart_from_wishlist'),
    path('add_all_to_cart_from_wishlist/', views.add_all_to_cart_form_wishlist, name='add_all_to_cart_from_wishlist'),


    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<str:slug>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<str:slug>/', views.remove_from_cart, name='remove_from_cart'),
    path('add_quantity/<str:slug>/', views.add_quantity, name='add_quantity'),
    path('remove_quantity/<str:slug>/', views.remove_quantity, name='remove_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_quantity/<str:slug>/', views.update_quantity, name='update_cart'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove_coupon/', views.remove_coupon, name='remove_coupon'),
    path('track_orders/', views.track_orders, name='track_orders'),
    path('track_orders/search/', views.track_orders_search, name='track_orders_search'),
    path('track_orders/details/<int:order_id>/', views.track_order_details, name='track_order_details'),
    path('track_orders/download_invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('track_orders/cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('get_address/<int:address_id>/', views.get_address, name='get_address'),
    path('get_default_address/', views.get_default_address, name='get_default_address'),
]
