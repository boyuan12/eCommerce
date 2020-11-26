from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("create-shop/", views.create_shop)
]