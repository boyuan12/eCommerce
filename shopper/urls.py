from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("item/<uuid:item_id>/", views.view_item),
]