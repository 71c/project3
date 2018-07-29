from django.db import models
from django.contrib.auth.models import User

from orders.models import *

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    activation_key = models.CharField(max_length=255, default=1)
    email_validated = models.BooleanField(default=False)

    cart = models.ManyToManyField(Item, blank=True)