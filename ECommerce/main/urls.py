from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.update_profile, name='profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('change_password_done/', views.change_password_done, name='change_password_done'),
    path('logout/', views.logout, name='logout'),
]
