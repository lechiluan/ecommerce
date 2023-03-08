from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Customer(models.Model):
    REQUIRED_FIELDS = ('user',)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', unique=True)
    mobile = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=40, null=True)

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return self.user.first_name

    class Meta:
        db_table = "Customer"


class Product(models.Model):
    name = models.CharField(max_length=40)
    product_image = models.ImageField(upload_to='media/product_image/', null=True, blank=True)
    price = models.PositiveIntegerField()
    description = models.CharField(max_length=40)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Product"


class Brand(models.Model):
    name = models.CharField(max_length=40)
    logo = models.ImageField(upload_to='media/brand_logo/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Brand"


class Category(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Category"


class Coupon(models.Model):
    code = models.CharField(max_length=20)
    discount = models.PositiveIntegerField()

    def __str__(self):
        return self.code

    class Meta:
        db_table = "Coupon"


class Cart(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    amount = models.PositiveIntegerField()
    coupon = models.ForeignKey('Coupon', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.product.name

    class Meta:
        db_table = "Cart"


class Orders(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Order Confirmed', 'Order Confirmed'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
    )
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True)
    email = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=500, null=True)
    mobile = models.CharField(max_length=20, null=True)
    order_date = models.DateField(auto_now_add=True, null=True)
    status = models.CharField(max_length=50, null=True, choices=STATUS)
    coupon = models.ForeignKey('Coupon', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.product.name

    class Meta:
        db_table = "Orders"


class OrderDetails(models.Model):
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    amount = models.PositiveIntegerField()

    def __str__(self):
        return self.product.name

    class Meta:
        db_table = "OrderDetails"


class Contact(models.Model):
    name = models.CharField(max_length=40)
    email = models.CharField(max_length=50, null=True)
    phone = models.CharField(max_length=20, null=True)
    message = models.CharField(max_length=500)
    date = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Contact"


class Payment(models.Model):
    METHOD = ('Cash on Delivery', 'Cash on Delivery'), \
        ('Online Payment', 'Online Payment'), \
        ('Bank Transfer', 'Bank Transfer'), \
        ('Momo', 'Momo'), \
        ('Paypal', 'Paypal'), \
        ('Credit Card', 'Credit Card'), \
        ('Debit Card', 'Debit Card')
    PAYMENT = ('Pending', 'Pending'), \
        ('Paid', 'Paid')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    amount = models.PositiveIntegerField()
    payment_method = models.CharField(max_length=50, null=True, choices=METHOD)
    payment_date = models.DateField(auto_now_add=True, null=True)
    payment_status = models.CharField(max_length=50, null=True, choices=PAYMENT)

    def __str__(self):
        return self.product.name

    class Meta:
        db_table = "Payment"


class Review(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True)
    rate = models.PositiveIntegerField()
    message_review = models.CharField(max_length=500)

    def __str__(self):
        return self.product.name

    class Meta:
        db_table = "Review"

