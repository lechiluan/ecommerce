from django.db import models


class UserProfile(models.Model):
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=50)

    def __str__(self):
        return self.email


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='static/images/products/')

    def __str__(self):
        return self.name
