from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("create-shop/", views.create_shop),
    path("delete-item/", views.delete_item),
    path("shop/<uuid:shop_id>/add-item/", views.add_item),
    path("shop/<uuid:shop_id>/items/<uuid:item_id>/", views.view_item),
    path("shop/<uuid:shop_id>/", views.view_shop),
    path("shop/<uuid:shop_id>/orders/", views.view_orders),
    path("shop/<uuid:shop_id>/orders/<str:order_item>/", views.view_order),
]