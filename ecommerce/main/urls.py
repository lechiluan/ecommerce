from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
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
]
