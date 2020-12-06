from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("item/<uuid:item_id>/", views.view_item),
    path("add-cart/", views.add_cart),
    path("cart/", views.cart),
    path("delete-cart/", views.delete_cart),
    path("stripe/", views.stripe_payment),
    path("modify-item/", views.modify_cart),
    path("item-purchase/", views.get_all_cart_item),
    path("create-payment-intent/", views.create_payment_intent)
]