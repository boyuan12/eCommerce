from json.decoder import JSONDecodeError
from django.http.response import JsonResponse
from django.shortcuts import render
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from .models import Shop, Item, ItemPicture, StripeConnected
from django.http import HttpResponseRedirect, HttpResponse
import requests
from shopper.models import Order, OrderItem
from authentication.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import stripe
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = os.getenv("STRIPE_API_KEY")

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
    
    if len(OrderItem.objects.filter(item_id=item.item_id)) != 0:
        return HttpResponse("You can't delete a merchandise until you shipped all active orders")

    item.delete()
    return redirect("/seller")

@csrf_exempt
def onboard_user(request):
    origin = request.META.get("HTTP_ORIGIN")
    try:
        sc = StripeConnected.objects.get(user_id=request.user.id)
        return redirect("/seller/stripe-conn")

    except:
        return redirect(f"https://connect.stripe.com/express/oauth/v2/authorize?response_type=code&client_id=ca_IR3sv6l0BZhRMbdFUIxGaj6D7JPP6han&redirect_uri=http://ecommerce-python-django.herokuapp.com/seller/stripe-conn/finish-onboarding/")

def stripe_conn(request):
    try:
        sc = StripeConnected.objects.get(user_id=request.user.id)
        return HttpResponse("Account connected successfully, go back to <a href='/seller/'>dashboard</a>")
    except Exception as e:
        return render(request, "seller/stripe-conn.html")

def stripe_conn_finish_onboarding(request):
    code = request.GET.get("code")
    response = stripe.OAuth.token(
        grant_type='authorization_code',
        code=code,
    )

    # Access the connected account id in the response
    connected_account_id = response['stripe_user_id']

    StripeConnected.objects.filter(user_id=request.user.id).delete()
    StripeConnected.objects.create(user_id=request.user.id, stripe_acct_id=connected_account_id)

    return redirect("/seller/stripe-conn/")

@csrf_exempt
def payout(request):
    order_items = []
    _items = []

    total_merchandise = 0
    total_shipping = 0
    PLATFORM_FEE = 0.50
    
    shops = Shop.objects.filter(user_id=request.user.id)

    for shop in shops:
        items = Item.objects.filter(shop_id=shop.shop_id)
        for item in items:
            oi = OrderItem.objects.filter(item_id=item.item_id, is_payout=False)
            for o in oi:
                order_items.append(o)
                _items.append(item)

                total_merchandise += item.price
                total_shipping += item.shipping
    
    total_available = total_merchandise * PLATFORM_FEE + total_shipping


    if request.method == "POST":
        try:
            sc = StripeConnected.objects.get(user_id=request.user.id)
        except:
            return redirect("/seller/stripe-conn")

        transfer = stripe.Transfer.create(
            amount=int(total_available * 100),
            currency="usd",
            destination=sc.stripe_acct_id,
        )
        print(transfer)

        for item in order_items:
            item.is_payout = True
            item.save()
        
    else:


        return render(request, "seller/payout.html", {
            "total_merchandise": str(round(total_merchandise, 2)),
            "total_shipping": str(round(total_shipping, 2)),
            "platform_fee": str(round(PLATFORM_FEE * 100, 2)) + "%",
            "total_available": str(round(total_available, 2))
        })

