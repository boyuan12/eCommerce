from django.shortcuts import render
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from .models import Shop, Item, ItemPicture
from django.http import HttpResponseRedirect, HttpResponse
import requests


cloudinary.config(
    cloud_name="boyuan12",
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


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


def add_item(request, shop_id):
    if request.method == "POST":
        # USPS username: 699DEVWI7317
        if request.POST.get("zip") == '':
            Item(name=request.POST["name"], description=request.POST["description"], price=float(request.POST["price"]), shop_id=shop_id, zip=request.POST.get("zip"), usps_option=request.POST["usps"], shipping=request.POST["shipping"]).save()
        else:
            Item(name=request.POST["name"], description=request.POST["description"], price=float(request.POST["price"]), shop_id=shop_id, shipping=request.POST["shipping"], fastest_delivery=request.POST["fastest"], slowest_delivery=request.POST["slowest"]).save()
        item = Item.objects.filter(name=request.POST["name"], description=request.POST["description"], price=float(request.POST["price"]), shop_id=shop_id)[::-1][0]

        images = request.FILES.getlist('images')
        for i in images:
            r = cloudinary.uploader.upload(i)
            img_url = r["secure_url"]
            ItemPicture(item_id=item.item_id, img_url=img_url).save()

        return HttpResponseRedirect(f"/seller/shop/{shop_id}/items/{item.item_id}")
    else:
        return render(request, "seller/add-item.html")


def view_item(request, shop_id, item_id):
    shop = Shop.objects.get(shop_id=shop_id)
    item = Item.objects.get(item_id=item_id)
    images = ItemPicture.objects.filter(item_id=item_id)

    return render(request, "seller/view-item.html", {
        "shop": shop,
        "item": item,
        "image0": images[0],
        "images": images[1:]
    })
