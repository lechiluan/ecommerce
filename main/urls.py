from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('terms_and_conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('activate_email/<uidb64>/<token>/', views.activate_new_email, name='activate_email'),
    path('login/', views.login, name='login'),
    path('profile/', views.update_profile, name='profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('logout/', views.logout, name='logout'),
    path("password_reset/", views.password_reset_request, name="password_reset"),
    path('change_email/', views.change_email, name='change_email'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="registration/password/password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password/password_reset_complete.html'),
         name='password_reset_complete'),

    # Address Books
    path('delivery_address/', views.delivery_address_table, name='address_book'),
    path('delivery_address/add/', views.add_delivery_address, name='add_address'),
    path('delivery_address/update/<int:delivery_address_id>/', views.update_delivery_address, name='update_address'),
    path('delivery_address/delete/<int:delivery_address_id>/', views.delete_delivery_address, name='delete_address'),
    path('delivery_address/delete_selected/<str:delivery_address_ids>/', views.delete_selected_delivery_address,
         name='delete_selected_address'),
    path('delivery_address/set_default/<int:delivery_address_id>/', views.set_default_delivery_address,
         name='set_default_address'),
    path('delivery_address/search/', views.search_delivery_address, name='address_search'),
]
