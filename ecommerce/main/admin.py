from django.contrib import admin
from django.contrib.auth.models import Permission
from main.models import Category, Contact, Coupon, Customer, Product, Review, Payment, Orders, \
    OrderDetails, CartItem, Brand

# Register your models here.
admin.site.register(Permission)
admin.site.site_header = 'Ecommerce Admin Dashboard'
admin.site.site_title = 'Ecommerce Admin Dashboard'
admin.site.index_title = 'Welcome to Ecommerce Admin Dashboard'

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Orders)
admin.site.register(Review)
admin.site.register(Payment)
admin.site.register(OrderDetails)
admin.site.register(CartItem)
admin.site.register(Contact)
admin.site.register(Coupon)
admin.site.register(Category)
admin.site.register(Brand)
