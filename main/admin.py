from django.contrib import admin
from django.contrib.auth.models import Permission
from main.models import Category, Feedback, Coupon, Customer, Product, Review, Payment, Orders, \
    OrderDetails, CartItem, Brand, DeliveryAddress, Wishlist
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Customize the admin site
admin.site.register(Permission)
admin.site.index_title = 'LCL Shop - Admin Dashboard'
admin.site.site_header = 'LCL Shop - Admin Dashboard'
admin.site.site_title = 'LCL Shop - Admin Dashboard'


class CustomUserAdmin(UserAdmin):
    # Customize the display of fields in the admin list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')

    # Customize the available filters in the admin list view
    list_filter = ('is_staff', 'is_superuser', 'groups')

    # Customize the search fields available in the admin search bar
    search_fields = ('username', 'email', 'first_name', 'last_name')

    # Customize the default sorting order of items in the admin list view
    ordering = ('username',)

    # Customize the layout and order of fields on the User edit page
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Customize the layout of fields on the User add page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


# Unregister the default User admin
admin.site.unregister(User)

# Register the customized User admin
admin.site.register(User, CustomUserAdmin)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name', 'mobile', 'address']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'mobile', 'address']
    list_filter = ['user__date_joined', 'user__is_active']
    readonly_fields = ['get_id']

    def get_id(self, obj):
        return obj.user.id

    get_id.short_description = 'ID'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'description']
    search_fields = ['name', 'description']
    list_filter = ['name']
    readonly_fields = ['get_id']

    def get_id(self, obj):
        return obj.id

    get_id.short_description = 'ID'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'description', 'logo']
    search_fields = ['name', 'description']
    list_filter = ['name']
    readonly_fields = ['get_id']

    def get_id(self, obj):
        return obj.id

    get_id.short_description = 'ID'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'price', 'old_price', 'stock', 'sold', 'view_count']
    search_fields = ['name', 'category__name', 'brand__name']
    list_filter = ['category', 'brand', 'price', 'old_price', 'stock']
    readonly_fields = ['get_id']

    def get_id(self, obj):
        return obj.id

    get_id.short_description = 'ID'


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ['customer', 'order_date', 'status', 'sub_total', 'total_discount', 'total_amount']
    list_filter = ['status']
    search_fields = ['customer__username']
    date_hierarchy = 'order_date'


@admin.register(OrderDetails)
class OrderDetailsAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'sub_total', 'coupon', 'coupon_applied']
    list_filter = ['coupon_applied']
    search_fields = ['order__id', 'product__name']
    list_editable = ['coupon_applied']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount', 'amount', 'valid_from', 'valid_to', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code']
    date_hierarchy = 'valid_from'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'quantity', 'price', 'sub_total', 'coupon', 'coupon_applied']
    list_filter = ['coupon_applied']
    search_fields = ['customer__username', 'product__name']
    list_editable = ['coupon_applied']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'rate', 'date_added', 'review_status')
    list_filter = ('product', 'date_added', 'review_status')
    search_fields = ('customer__first_name', 'customer__last_name', 'product__name', 'message_review')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'order', 'payment_method', 'payment_status', 'total', 'transaction_id', 'payment_date']
    list_filter = ['payment_method', 'payment_status']
    search_fields = ['customer__name', 'order__id', 'transaction_id']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile', 'subject', 'date_sent')
    list_filter = ('date_sent',)
    search_fields = ('name', 'email', 'mobile', 'subject', 'message')
    ordering = ('-date_sent',)


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer', 'first_name', 'last_name', 'mobile', 'email', 'address', 'city', 'state', 'country',
        'zip_code',
        'is_default')
    list_filter = ('customer',)
    search_fields = (
        'customer__email', 'first_name', 'last_name', 'mobile', 'email', 'address', 'city', 'state', 'country',
        'zip_code')

    fieldsets = (
        ('Customer Info', {'fields': ('customer',)}),
        ('Contact Info', {'fields': ('first_name', 'last_name', 'mobile', 'email')}),
        ('Address', {'fields': ('address', 'city', 'state', 'country', 'zip_code')}),
        ('Default', {'fields': ('is_default',)}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(customer=request.user.customer)

    def save_model(self, request, obj, form, change):
        obj.customer = request.user.customer
        super().save_model(request, obj, form, change)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'date_added')
    list_filter = ('customer', 'product', 'date_added')
    search_fields = ('customer__username', 'product__name')
