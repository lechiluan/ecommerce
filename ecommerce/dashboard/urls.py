from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_home, name='index'),
    # Customer URL
    path('customer/', views.customer_table, name='user_customer_table'),
    path('customer/details/<int:user_id>/', views.customer_details, name='customer_details'),
    path('customer/add/', views.add_customer, name='add_customer'),
    path('customer/update/<int:user_id>/', views.update_customer, name='update_customer'),
    path('customer/update_password/<int:user_id>/', views.update_customer_password, name='update_customer_password'),
    path('customer/delete/<int:user_id>/', views.delete_customer, name='delete_customer'),
    path('customer/delete_selected/<str:customer_ids>/', views.delete_selected_customer,
         name='delete_selected_customer'),
    path('customer/search/', views.search_customer, name='search_customer'),

    # Category URL
    path('category/', views.category_table, name='category_table'),
    path('category/details/<int:category_id>/', views.category_details, name='category_details'),
    path('category/add/', views.add_category, name='add_category'),
    path('category/update/<int:category_id>/', views.update_category, name='update_category'),
    path('category/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('category/delete_selected/<str:category_ids>/', views.delete_selected_category,
         name='delete_selected_category'),
    path('category/search/', views.search_category, name='search_category'),

    # # Brand URL
    path('brand/', views.brand_table, name='brand_table'),
    path('brand/details/<int:brand_id>/', views.brand_details, name='brand_details'),
    path('brand/add/', views.add_brand, name='add_brand'),
    path('brand/update/<int:brand_id>/', views.update_brand, name='update_brand'),
    path('brand/delete/<int:brand_id>/', views.delete_brand, name='delete_brand'),
    path('brand/delete_selected/<str:brand_ids>/', views.delete_selected_brand,
         name='delete_selected_brand'),
    path('brand/search/', views.search_brand, name='search_brand'),
]
