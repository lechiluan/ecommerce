from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .views import email_confirmation, activate

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.update_profile, name='profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('change_password_done/', views.change_password_done, name='change_password_done'),
    path('logout/', views.logout, name='logout'),
    path("password_reset/", views.password_reset_request, name="password_reset"),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="registration/password/password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password/password_reset_complete.html'),
         name='password_reset_complete'),
    path('email-confirmation/', email_confirmation, name='email_confirmation'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
]
