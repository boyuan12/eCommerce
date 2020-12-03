from django.db import models
import uuid

# Create your models here.
class TwoFAToken(models.Model):
    user_id = models.IntegerField()
    code = models.CharField(max_length=7, unique=True)
    phone = models.CharField(null=True, max_length=20)


class TWOFAVerified(models.Model):
    user_id = models.IntegerField()
    phone = models.CharField(max_length=20)


class AuthorizedDevice(models.Model):
    user_id = models.IntegerField()
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)


class Profile(models.Model):
    user_id = models.IntegerField()
    role = models.IntegerField() # 0: shopper, 1: seller
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    zip = models.CharField(max_length=10)