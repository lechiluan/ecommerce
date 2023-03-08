from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.admin_home, name='index'),
    path('customer_table/', views.user_customer_table, name='user_customer_table'),
    path('delete_customer/<int:user_id>/', views.delete_customer, name='delete_customer'),
    path('search_customer/', views.search_customer, name='search_customer'),
    path('add_customer/', views.add_customer, name='add_customer'),
    path('update_customer/<int:user_id>', views.update_customer, name='update_customer'),
]
