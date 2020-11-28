from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("create-shop/", views.create_shop),
    path("shop/<uuid:shop_id>/add-item/", views.add_item),
    path("shop/<uuid:shop_id>/items/<uuid:item_id>/", views.view_item)
]