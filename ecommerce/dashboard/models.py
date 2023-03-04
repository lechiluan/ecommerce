from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Custommer(models.Model):
    # add additional fields in here
    phone = models.CharField(max_length=10, blank=True)
    address = models.CharField(max_length=100, blank=True)

    # link User to the default User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

