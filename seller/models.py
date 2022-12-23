from django.db import models
import uuid

# Create your models here.
class Shop(models.Model):
    shop_id = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    logo = models.CharField(max_length=255)
    user_id = models.IntegerField()


class Item(models.Model):
    item_id = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    price = models.FloatField()
    shop_id = models.UUIDField()
    zip = models.CharField(max_length=5, null=True)
    usps_option = models.CharField(max_length=20, null=True)
    fastest_delivery = models.CharField(max_length=25, null=True)
    slowest_delivery = models.CharField(max_length=25, null=True)
    shipping = models.FloatField()


class ItemPicture(models.Model):
    item_id = models.UUIDField(default=uuid.uuid4)
    img_url = models.CharField(max_length=255)

class StripeConnected(models.Model):
    user_id = models.IntegerField()
    stripe_acct_id = models.CharField(max_length=255)
