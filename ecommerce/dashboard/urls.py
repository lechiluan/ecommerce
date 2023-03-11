from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_home, name='index'),
    path('customer_table/', views.user_customer_table, name='user_customer_table'),
    path('customer_details/<int:user_id>/', views.customer_details, name='customer_details'),
    path('add_customer/', views.add_customer, name='add_customer'),
    path('update_customer/<int:user_id>', views.update_customer, name='update_customer'),
    path('delete_customer/<int:user_id>/', views.delete_customer, name='delete_customer'),
    path('delete_selected_customer/<str:customer_ids>/', views.delete_selected_customer, name='delete_selected_customer'),
    path('search_customer/', views.search_customer, name='search_customer'),
]
