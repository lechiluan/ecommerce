from django.contrib import admin
from django.contrib.auth.models import Permission
from main.models import *

# Register your models here.
admin.site.register(Permission)
admin.site.site_header = 'Ecommerce Admin Dashboard'
admin.site.site_title = 'Ecommerce Admin Dashboard'
admin.site.index_title = 'Welcome to Ecommerce Admin Dashboard'
