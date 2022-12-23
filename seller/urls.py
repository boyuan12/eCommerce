from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("create-shop/", views.create_shop),
    path("delete-item/", views.delete_item),
    path("stripe-conn/onboard-user/", views.onboard_user),
    path("stripe-conn/onboard-user/refresh/", views.onboard_user_refresh),
    path("stripe-conn/finish-onboarding/", views.stripe_conn_finish_onboarding),
    path("stripe-conn/", views.stripe_conn),
    path("payout/", views.payout),
    path("shop/<uuid:shop_id>/add-item/", views.add_item),
    path("shop/<uuid:shop_id>/items/<uuid:item_id>/", views.view_item),
    path("shop/<uuid:shop_id>/", views.view_shop),
    path("shop/<uuid:shop_id>/orders/", views.view_orders),
    path("shop/<uuid:shop_id>/orders/<str:order_item>/", views.view_order),
]