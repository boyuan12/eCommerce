from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("item/<uuid:item_id>/", views.view_item),
    path("add-cart/", views.add_cart),
    path("cart/", views.cart),
    path("delete-cart/", views.delete_cart)
]