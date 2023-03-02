from django.urls import path, include
from . import views

urlpatterns = [
    path('home/', views.admin_home, name='index'),
]