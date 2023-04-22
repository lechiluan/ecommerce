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
    path('chatbot/', views.chatbot, name='chatbot'),

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
    path('customer/export/csv/', views.export_customer_csv, name='export_customer_csv'),
    path('customer/export/excel/', views.export_customer_excel, name='export_customer_excel'),
    path('customer/export/json/', views.export_customer_json, name='export_customer_json'),

    # Category URL
    path('category/', views.category_table, name='category_table'),
    path('category/details/<int:category_id>/', views.category_details, name='category_details'),
    path('category/add/', views.add_category, name='add_category'),
    path('category/update/<int:category_id>/', views.update_category, name='update_category'),
    path('category/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('category/delete_selected/<str:category_ids>/', views.delete_selected_category,
         name='delete_selected_category'),
    path('category/search/', views.search_category, name='search_category'),
    path('category/export/csv/', views.export_category_csv, name='export_category_csv'),
    path('category/export/excel/', views.export_category_excel, name='export_category_excel'),
    path('category/export/json/', views.export_category_json, name='export_category_json'),

    # Brand URL
    path('brand/', views.brand_table, name='brand_table'),
    path('brand/details/<int:brand_id>/', views.brand_details, name='brand_details'),
    path('brand/add/', views.add_brand, name='add_brand'),
    path('brand/update/<int:brand_id>/', views.update_brand, name='update_brand'),
    path('brand/delete/<int:brand_id>/', views.delete_brand, name='delete_brand'),
    path('brand/delete_selected/<str:brand_ids>/', views.delete_selected_brand,
         name='delete_selected_brand'),
    path('brand/search/', views.search_brand, name='search_brand'),
    path('brand/export/csv/', views.export_brand_csv, name='export_brand_csv'),
    path('brand/export/excel/', views.export_brand_excel, name='export_brand_excel'),
    path('brand/export/json/', views.export_brand_json, name='export_brand_json'),

    # Product URL
    path('product/', views.product_table, name='product_table'),
    path('product/details/<int:product_id>/', views.product_details, name='product_details'),
    path('product/add/', views.add_product, name='add_product'),
    path('product/update/<int:product_id>/', views.update_product, name='update_product'),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('product/delete_selected/<str:product_ids>/', views.delete_selected_product,
         name='delete_selected_product'),
    path('product/search/', views.search_product, name='search_product'),
    path('product/export/csv/', views.export_product_csv, name='export_product_csv'),
    path('product/export/excel/', views.export_product_excel, name='export_product_excel'),
    path('product/export/json/', views.export_product_json, name='export_product_json'),

    # Coupon URL
    path('coupon/', views.coupon_table, name='coupon_table'),
    path('coupon/details/<int:coupon_id>/', views.coupon_details, name='coupon_details'),
    path('coupon/add/', views.add_coupon, name='add_coupon'),
    path('coupon/update/<int:coupon_id>/', views.update_coupon, name='update_coupon'),
    path('coupon/delete/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),
    path('coupon/delete_selected/<str:coupon_ids>/', views.delete_selected_coupon,
         name='delete_selected_coupon'),
    path('coupon/search/', views.search_coupon, name='search_coupon'),
    path('coupon/export/csv/', views.export_coupon_csv, name='export_coupon_csv'),
    path('coupon/export/excel/', views.export_coupon_excel, name='export_coupon_excel'),
    path('coupon/export/json/', views.export_coupon_json, name='export_coupon_json'),

    # Order URL
    path('order/', views.order_table, name='order_table'),
    path('order/details/<int:order_id>/', views.order_details, name='order_details'),
    path('order/update_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('order/delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('order/delete_selected/<str:order_ids>/', views.delete_selected_order,
         name='delete_selected_order'),
    path('order/search/', views.search_order, name='search_order'),
    path('order/download_invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('order/export/csv/', views.export_order_csv, name='export_order_csv'),
    path('order/export/excel/', views.export_order_excel, name='export_order_excel'),
    path('order/export/json/', views.export_order_json, name='export_order_json'),

    # Feedback URL
    path('feedback/', views.feedback_table, name='feedback_table'),
    path('feedback/details/<int:feedback_id>/', views.feedback_details, name='feedback_details'),
    path('feedback/delete/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),
    path('feedback/delete_selected/<str:feedback_ids>/', views.delete_selected_feedback,
         name='delete_selected_feedback'),
    path('feedback/search/', views.search_feedback, name='search_feedback'),
    path('feedback/export/csv/', views.export_feedback_csv, name='export_feedback_csv'),
    path('feedback/export/excel/', views.export_feedback_excel, name='export_feedback_excel'),
    path('feedback/export/json/', views.export_feedback_json, name='export_feedback_json'),

    # Payment URL
    path('payment/', views.payment_table, name='payment_table'),
    path('payment/details/<int:payment_id>/', views.payment_details, name='payment_details'),
    path('payment/search/', views.search_payment, name='search_payment'),
    path('payment/update_status/<int:payment_id>/', views.update_payment_status, name='update_payment_status'),
    path('payment/export/csv/', views.export_payment_csv, name='export_payment_csv'),
    path('payment/export/excel/', views.export_payment_excel, name='export_payment_excel'),
    path('payment/export/json/', views.export_payment_json, name='export_payment_json'),

    # Review URL
    path('review/', views.review_table, name='review_table'),
    path('review/details/<int:review_id>/', views.review_details, name='review_details'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('review/delete_selected/<str:review_ids>/', views.delete_selected_review,
         name='delete_selected_review'),
    path('review/search/', views.search_review, name='search_review'),
    path('review/change_status/<int:review_id>/', views.change_review_status, name='change_review_status'),
    path('review/export/csv/', views.export_review_csv, name='export_review_csv'),
    path('review/export/excel/', views.export_review_excel, name='export_review_excel'),
    path('review/export/json/', views.export_review_json, name='export_review_json'),

    # Sales Statistics URL
    path('sales_statistics/', views.sales_statistics, name='sales_statistics'),
    path('sales_statistics/filter/', views.sales_statistics_filter, name='sales_statistics_filter'),
]
