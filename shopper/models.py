from django.contrib.auth.models import User
from django.db import models
from seller.models import Item

# Create your models here.
class PageView(models.Model):
    item_id = models.UUIDField()
    timestamp = models.DateTimeField(auto_now=True)


class CartItem(models.Model):
    item_id = models.UUIDField()
    user_id = models.IntegerField()
    quantity = models.IntegerField()


class Order(models.Model):
    payment_id = models.CharField(max_length=100)
    user_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    item_id = models.UUIDField()
    quantity = models.IntegerField()
    payment_id = models.CharField(max_length=100)
    order_status = models.IntegerField() # 0: waiting to be shipped, 1: shipped, 2: arrived
    tracking_number = models.CharField(max_length=100, null=True)
    shipping_company = models.CharField(max_length=100, null=True)
    website = models.CharField(max_length=255, null=True)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_id = models.UUIDField()
    rating = models.IntegerField()
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
