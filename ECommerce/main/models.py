from django.db import models


# Create your models here.
# class Category(models.Model):
#     name = models.CharField(max_length=50)
#     description = models.TextField()
#     def __str__(self):
#         return self.name
# class Product(models.Model):
#     name = models.CharField(max_length=50)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     description = models.TextField()
#     image = models.ImageField(upload_to='static/images/products/')
#     def __str__(self):
#         return self.name

# class Customer(models.Model):
#     name = models.CharField(max_length=50)
#     email = models.EmailField()
#     password = models.CharField(max_length=50)
#     telephone = models.CharField(max_length=10)
#     address = models.CharField(max_length=100)
#     role = models.ForeignKey('Role', on_delete=models.CASCADE)
#     def __str__(self):
#         return self.name
# class Role(models.Model):
#     name = models.CharField(max_length=50)
#     def __str__(self):
#         return self.name
# class Product(models.Model):
#     name = models.CharField(max_length=50)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     description = models.TextField()
#     image = models.ImageField(upload_to='static/images/products/')
#     def __str__(self):
#         return self.name
# class Order(models.Model):
#     customer = models.ForeignKey('customer', on_delete=models.CASCADE)
#     product = models.ForeignKey('Product', on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#     def __str__(self):
#         return self.customer.name + ' - ' + self.product.name
# class OrderDetail(models.Model):
#     order = models.ForeignKey('Order', on_delete=models.CASCADE)
#     product = models.ForeignKey('Product', on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#     def __str__(self):
#         return self.order.customer.name + ' - ' + self.product.name
# class Category(models.Model):
#     name = models.CharField(max_length=50)
#     description = models.TextField()
#     def __str__(self):
#         return self.name
# class ProductCategory(models.Model):
#     product = models.ForeignKey('Product', on_delete=models.CASCADE)
#     category = models.ForeignKey('Category', on_delete=models.CASCADE)
#     def __str__(self):
#         return self.product.name + ' - ' + self.category.name
# class Comment(models.Model):
#     customer = models.ForeignKey('customer', on_delete=models.CASCADE)
#     product = models.ForeignKey('Product', on_delete=models.CASCADE)
#     content = models.TextField()
#     def __str__(self):
#         return self.customer.name + ' - ' + self.product.name
# class Rating(models.Model):
#     customer = models.ForeignKey('customer', on_delete=models.CASCADE)
#     product = models.ForeignKey('Product', on_delete=models.CASCADE)
#     rating = models.IntegerField()
#     def __str__(self):
#         return self.customer.name + ' - ' + self.product.name
# class Cart(models.Model):
#     customer = models.ForeignKey('customer', on_delete=models.CASCADE)
#     product = models.ForeignKey('Product', on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#     def __str__(self):
#         return self.customer.name + ' - ' + self.product.name
# class CartDetail(models.Model):
#     cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
#     product = models.ForeignKey('Product', on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#     def __str__(self):
#         return self.cart.customer.name + ' - ' + self.product.name
# class Payment(models.Model):
#     customer = models.ForeignKey('customer', on_delete=models.CASCADE)
#     order = models.ForeignKey('Order', on_delete=models.CASCADE)
#     payment_method = models.CharField(max_length=50)
#     def __str__(self):
#         return self.customer.name + ' - ' + self.order.product.name
# class PaymentDetail(models.Model):
#     payment = models.ForeignKey('Payment', on_delete=models.CASCADE)
#     order = models.ForeignKey('Order', on_delete=models.CASCADE)
#     payment_method = models.CharField(max_length=50)
#     def __str__(self):
#         return self.payment.customer.name + ' - ' + self.order.product.name
# class Shipping(models.Model):
#     customer = models.ForeignKey('customer', on_delete=models.CASCADE)
#     order = models.ForeignKey('Order', on_delete=models.CASCADE)
#     address = models.CharField(max_length=100)
#     def __str__(self):
#         return self.customer.name + ' - ' + self.order.product.name
# class ShippingDetail(models.Model):
#     shipping = models.ForeignKey('Shipping', on_delete=models.CASCADE)
#     order = models.ForeignKey('Order', on_delete=models.CASCADE)
#     address = models.CharField(max_length=100)
#     def __str__(self):
#         return self.shipping.customer.name + ' - ' + self.order.product.name
# class Coupon(models.Model):
#     code = models.CharField(max_length=50)
#     discount = models.IntegerField()
#     def __str__(self):
#         return self.code
# class CouponDetail(models.Model):
#     coupon = models.ForeignKey('Coupon', on_delete=models.CASCADE)
#     order = models.ForeignKey('Order', on_delete=models.CASCADE)
#     def __str__(self):
#         return self.coupon.code + ' - ' + self.order.product.name
# class ProductTag(models.Model):
#     product = models.ForeignKey('Product', on_delete=models.CASCADE)
#     tag = models.CharField(max_length=50)
#     def __str__(self):
#         return self.product.name + ' - ' + self.tag
