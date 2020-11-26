from django.shortcuts import render
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from .models import Shop
from django.http import HttpResponseRedirect

cloudinary.config(
    cloud_name="boyuan12",
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Create your views here.
def index(request):
    shops = Shop.objects.filter(user_id=request.user.id)
    return render(request, "seller/index.html", {
        "shops": shops
    })


def create_shop(request):
    if request.method == "POST":
        name = request.POST["name"]
        description = request.POST["description"]

        r = cloudinary.uploader.upload(request.FILES["logo"])
        img_url = r["secure_url"]

        Shop(name=name, description=description, logo=img_url, user_id=request.user.id).save()

        return HttpResponseRedirect("/seller/")

    else:
        return render(request, "seller/create-shop.html")


def add_item(request):
    if request.method == "POST":
        pass

    else:
        return render(request, "seller/add-item.html")

