from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='index'),

    # Administration URL
    path('profile/', views.update_profile, name='profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('change_email/', views.change_email, name='change_email'),
    path('activate_email_admin/<uidb64>/<token>/', views.activate_new_email_admin, name='activate_email_admin'),
    path('logout/', views.logout, name='logout'),

    # Customer URL
    path('customer/', views.customer_table, name='user_customer_table'),
    path('customer/details/<int:user_id>/', views.customer_details, name='customer_details'),
    path('customer/add/', views.add_customer, name='add_customer'),
    path('customer/update/<int:user_id>/', views.update_customer, name='update_customer'),
    path('customer/update_password/<int:user_id>/', views.update_customer_password, name='update_customer_password'),
    path('customer/delete/<int:user_id>/', views.delete_customer, name='delete_customer'),
    path('customer/delete_selected/<str:customer_ids>/', views.delete_selected_customer,
         name='delete_selected_customer'),
    path('customer/search/', views.search_customer, name='search_customer'),

    # Category URL
    path('category/', views.category_table, name='category_table'),
    path('category/details/<int:category_id>/', views.category_details, name='category_details'),
    path('category/add/', views.add_category, name='add_category'),
    path('category/update/<int:category_id>/', views.update_category, name='update_category'),
    path('category/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('category/delete_selected/<str:category_ids>/', views.delete_selected_category,
         name='delete_selected_category'),
    path('category/search/', views.search_category, name='search_category'),

    # Brand URL
    path('brand/', views.brand_table, name='brand_table'),
    path('brand/details/<int:brand_id>/', views.brand_details, name='brand_details'),
    path('brand/add/', views.add_brand, name='add_brand'),
    path('brand/update/<int:brand_id>/', views.update_brand, name='update_brand'),
    path('brand/delete/<int:brand_id>/', views.delete_brand, name='delete_brand'),
    path('brand/delete_selected/<str:brand_ids>/', views.delete_selected_brand,
         name='delete_selected_brand'),
    path('brand/search/', views.search_brand, name='search_brand'),

    # Product URL
    path('product/', views.product_table, name='product_table'),
    path('product/details/<int:product_id>/', views.product_details, name='product_details'),
    path('product/add/', views.add_product, name='add_product'),
    path('product/update/<int:product_id>/', views.update_product, name='update_product'),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('product/delete_selected/<str:product_ids>/', views.delete_selected_product,
         name='delete_selected_product'),
    path('product/search/', views.search_product, name='search_product'),

    # Coupon URL
    path('coupon/', views.coupon_table, name='coupon_table'),
    path('coupon/details/<int:coupon_id>/', views.coupon_details, name='coupon_details'),
    path('coupon/add/', views.add_coupon, name='add_coupon'),
    path('coupon/update/<int:coupon_id>/', views.update_coupon, name='update_coupon'),
    path('coupon/delete/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),
    path('coupon/delete_selected/<str:coupon_ids>/', views.delete_selected_coupon,
         name='delete_selected_coupon'),
    path('coupon/search/', views.search_coupon, name='search_coupon'),

    # Order URL
    path('order/', views.order_table, name='order_table'),
    path('order/details/<int:order_id>/', views.order_details, name='order_details'),
    # path('order/payment/<int:order_id>/', views.order_payment, name='order_payment'),

    # Feedback URL
    path('feedback/', views.feedback_table, name='feedback_table'),
    path('feedback/details/<int:feedback_id>/', views.feedback_details, name='feedback_details'),
    path('feedback/delete/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),
    path('feedback/delete_selected/<str:feedback_ids>/', views.delete_selected_feedback,
         name='delete_selected_feedback'),
    path('feedback/search/', views.search_feedback, name='search_feedback'),


    # Export URL
    # path('export/customer/csv/', views.export_customer_csv, name='export_customer_csv'),
    # path('export/customer/xls/', views.export_customer_xls, name='export_customer_xls'),
    # path('export/category/csv/', views.export_category_csv, name='export_category_csv'),
    # path('export/category/xls/', views.export_category_xls, name='export_category_xls'),
    # path('export/brand/csv/', views.export_brand_csv, name='export_brand_csv'),
    # path('export/brand/xls/', views.export_brand_xls, name='export_brand_xls'),
    # path('export/product/csv/', views.export_product_csv, name='export_product_csv'),
    # path('export/product/xls/', views.export_product_xls, name='export_product_xls'),
    # path('export/coupon/csv/', views.export_coupon_csv, name='export_coupon_csv'),
    # path('export/coupon/xls/', views.export_coupon_xls, name='export_coupon_xls'),
    # path('export/order/csv/', views.export_order_csv, name='export_order_csv'),
    # path('export/order/xls/', views.export_order_xls, name='export_order_xls'),
    # path('export/feedback/csv/', views.export_feedback_csv, name='export_feedback_csv'),
    # path('export/feedback/xls/', views.export_feedback_xls, name='export_feedback_xls'),
]
