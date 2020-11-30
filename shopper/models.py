from django.db import models

# Create your models here.
class PageView(models.Model):
    item_id = models.UUIDField()
    timestamp = models.DateTimeField(auto_now=True)
