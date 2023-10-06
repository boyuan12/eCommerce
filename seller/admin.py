from django.contrib import admin
from .models import Item, StripeConnected

# Register your models here.
admin.site.register(Item)
admin.site.register(StripeConnected)
