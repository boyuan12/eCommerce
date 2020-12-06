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

    def total(self):
        return self.quantity * Item.objects.get(item_id=self.item_id).price