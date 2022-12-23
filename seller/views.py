from json.decoder import JSONDecodeError
from django.http.response import JsonResponse
from django.shortcuts import render
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from .models import Shop, Item, ItemPicture
from django.http import HttpResponseRedirect, HttpResponse
import requests
from shopper.models import Order, OrderItem
from authentication.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

cloudinary.config(
    cloud_name="boyuan12",
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


@login_required(login_url='/auth/login')
def index(request):
    shops = Shop.objects.filter(user_id=request.user.id)
    return render(request, "seller/index.html", {
        "shops": shops
    })

@login_required(login_url='/auth/login')
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

@login_required(login_url='/auth/login')
def add_item(request, shop_id):
    shop = Shop.objects.get(shop_id=shop_id)
    if shop.user_id != request.user.id:
        return HttpResponse("403")

    if request.method == "POST":
        if request.POST.get("zip") != '':
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

@login_required(login_url='/auth/login')
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

@login_required(login_url='/auth/login')
def view_shop(request, shop_id):
    shop = Shop.objects.get(shop_id=shop_id)
    if shop.user_id != request.user.id:
        return HttpResponse("403")

    items = Item.objects.filter(shop_id=shop_id)
    data = []

    for item in items:
        order = OrderItem.objects.filter(item_id=item.item_id, order_status=0)
        if len(order) != 0:
            data.append([o for o in order])

    items_data = []
    for item in items:
        img = ItemPicture.objects.filter(item_id=item.item_id)[0]
        items_data.append([item, img])

    return render(request, "seller/shop.html", {
        "data": data,
        "data_length": len(data),
        "items": items_data
    })

@login_required(login_url='/auth/login')
def view_orders(request, shop_id):
    shop = Shop.objects.get(shop_id=shop_id)
    if shop.user_id != request.user.id:
        return HttpResponse("403")

    items = Item.objects.filter(shop_id=shop_id)
    data = []

    for item in items:
        order = OrderItem.objects.filter(item_id=item.item_id, order_status=0)
        if len(order) != 0:
            data.append([o for o in order])

    print(data)

    return render(request, "seller/orders.html", {
        "data": data,
        "data_length": len(data)
    })


@login_required(login_url='/auth/login')
def view_order(request, shop_id, order_item):
    shop = Shop.objects.get(shop_id=shop_id)
    if shop.user_id != request.user.id:
        return HttpResponse("403")

    if request.method == "POST":
        tracking_number = request.POST["tracking-number"]
        shipping_company = request.POST["shipping-company"]
        website = request.POST["website"]
        order_item_2 = OrderItem.objects.get(id=order_item)

        order_item_2.tracking_number = tracking_number
        order_item_2.shipping_company = shipping_company
        order_item_2.website = website
        order_item_2.order_status = 1
        order_item_2.save()

        return HttpResponseRedirect(f"/seller/shop/{shop_id}/orders/{order_item}")

    else:
        order_item_2 = OrderItem.objects.get(id=order_item)
        order = Order.objects.get(payment_id=order_item_2.payment_id)
        user = User.objects.get(id=order.user_id)
        profile = Profile.objects.get(user_id=order.user_id)
        item = Item.objects.get(item_id=order_item_2.item_id)


        return render(request, "seller/order.html", {
            "order_item": order_item_2,
            "order": order,
            "profile": profile,
            "item": item,
            "user": user
        })

@login_required(login_url='/auth/login')
def delete_item(request):
    id = request.GET.get("id")
    item = Item.objects.get(id=id)
    shop_id = item.shop_id
    s = Shop.objects.get(shop_id=shop_id)

    if s.user_id != request.user.id:
        return HttpResponse("403")

    item.delete()
    return redirect("/seller")