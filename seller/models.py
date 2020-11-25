from django.db import models
import uuid

# Create your models here.
class Shop(models.Model):
    shop_id = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    logo = models.CharField(max_length=255)
