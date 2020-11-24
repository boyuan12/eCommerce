from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register),
    path("login/", views.login_view),
    path("logout/", views.logout_view),
    path("2fa_verify/", views.complete_2fa),
    path("2fa/", views.twofa_verify)
]