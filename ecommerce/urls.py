"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from main import views as main_views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.shortcuts import render


# 404 error handler
def error_404(request, exception):
    return render(request, 'main/base/404.html', {})


handler404 = 'ecommerce.urls.error_404'

urlpatterns = [
    path('', main_views.home, name='index'),
    path('admin/lclshop/', admin.site.urls),  # admin site of django
    path('dashboard/', include('dashboard.urls')),  # dashboard admin site custom
    path('auth/', include('main.urls')),  # auth site custom to process authentication
    path('customer/', include('customer.urls')),  # customer site custom to process customer data order, cart.
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
