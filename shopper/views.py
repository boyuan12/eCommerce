import datetime
from typing import Any, List
from django.shortcuts import render
from seller.models import Item, ItemPicture
from .models import PageView, CartItem
import requests
import xmltodict
import json
from authentication.models import Profile
import datetime
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseRedirect
import json
import stripe


stripe.api_key = os.getenv("STRIPE_API_KEY")

def calculate_order_amount(items):
    """
        items: [["item-id", quantity]]
    """
    price = 0
    items = list(items)

    for i in items:
        item = Item.objects.get(item_id=i[0])
        price += float(item.price) * float(i[1]) + float(item.shipping)

    return int(price * 100)



# from django.http import HttpRequest

# Create your views here.

USPS_USERNAME = os.getenv("USPS_USERNAME")

# Create your views here.
def usps_estimate_delivery(service, origin, destination):
    r = requests.get(f'https://secure.shippingapis.com/ShippingAPI.dll?API={service}&XML=<{service}Request USERID="{USPS_USERNAME}"> <OriginZip>{origin}</OriginZip> <DestinationZip>{destination}</DestinationZip> </{service}Request>')
    data_dict = xmltodict.parse(r.text)
    json_data = json.dumps(data_dict)
    return json.loads(json_data)[service + "Response"]["Days"]


def sort_item(queryset):
    results = {}
    for i in queryset:
        try:
            results[i.item_id] = results[i.item_id] + 1
        except KeyError:
            results[i.item_id] = 1
    return results


def index(request):
    if request.GET.get("q") is not None:
        query = request.GET.get("q")
        results = []
        items = Item.objects.filter(name__contains=query) | \
                Item.objects.filter(description__contains=query) | \
                Item.objects.filter(item_id__contains=query)

        for i in items:
            item_pic = ItemPicture.objects.filter(item_id=i.item_id)[0]
            results.append([item_pic, i])

        return render(request, "shopper/searched.html", {
            "items": results,
            "q": query
        })
    else:

        current_hour = datetime.datetime.now().hour
        current_date = datetime.datetime.now().day

        try:
            PageView.objects.exclude(timestamp__day=current_date, timestamp__hour=current_hour).delete()
        except Exception as e:
            print(e)
            PageView.objects.filter(timestamp__hour=str(current_hour)).delete()

        popular_items = []
        result = sort_item(PageView.objects.filter())
        print(result)
        for i in result:
            item = Item.objects.get(item_id=i)
            pic = ItemPicture.objects.filter(item_id=item.item_id)[0]
            popular_items.append([item, result[i], pic])

        return render(request, "shopper/index.html", {
            "popular": popular_items
        })


def view_item(request, item_id):
    item = Item.objects.get(item_id=item_id)
    images = ItemPicture.objects.filter(item_id=item_id)
    in_cart = False

    try:
        CartItem.objects.get(item_id=item_id, user_id=request.user.id)
        in_cart = True
    except:
        pass

    PageView(item_id=item_id).save()
    p = Profile.objects.get(user_id=request.user.id)

    est = None
    est1 = None
    est2 = None

    if item.zip != '' and p.country == "United States of America":
        day = usps_estimate_delivery(item.usps_option, item.zip, p.zip)
        est = datetime.datetime.now() + datetime.timedelta(int(day))

    else:
        est1 = datetime.datetime.now() + datetime.timedelta(int(item.fastest_delivery))
        est2 = datetime.datetime.now() + datetime.timedelta(int(item.slowest_delivery))

    return render(request, "shopper/view-item.html", {
        "item": item,
        "image0": images[0],
        "images": images[1:],
        "est": est,
        "est1": est1,
        "est2": est2,
        "in_cart": in_cart
    })


@csrf_exempt
def add_cart(request):

    post_data = json.loads(request.body.decode("utf-8"))
    # https://stackoverflow.com/questions/61543829/django-taking-values-from-post-request-javascript-fetch-api

    item_id = post_data["item_id"]
    quantity = post_data["quantity"]
    user_id = request.user.id

    CartItem(item_id=item_id, user_id=user_id, quantity=quantity).save()

    return JsonResponse({"code": 200})


def cart(request):
    data = []
    items = CartItem.objects.filter(user_id=request.user.id)
    price = 0

    for i in items:
        item = Item.objects.get(item_id=i.item_id)
        pic = ItemPicture.objects.filter(item_id=i.item_id)[0]
        data.append([item, i, pic])
        print(i.quantity)
        price += (item.price * i.quantity + item.shipping)

    return render(request, "shopper/cart.html", {
        "data": data,
        "price": '%.2f' % round(price, 2)
    })


@csrf_exempt
def delete_cart(request):

    post_data = json.loads(request.body.decode("utf-8"))
    # https://stackoverflow.com/questions/61543829/django-taking-values-from-post-request-javascript-fetch-api

    item_id = post_data["item_id"]
    user_id = request.user.id

    CartItem.objects.get(item_id=item_id, user_id=user_id).delete()

    return JsonResponse({"code": 200})


@csrf_exempt
def modify_cart(request):

    post_data = json.loads(request.body.decode("utf-8"))
    item_id = post_data["item_id"]
    user_id = request.user.id
    quantity = post_data["quantity"]

    c = CartItem.objects.get(user_id=user_id, item_id=item_id)
    c.quantity = quantity
    c.save()

    return JsonResponse({"code": 200})


@csrf_exempt
def create_payment_intent(request):
    data = json.loads(request.body.decode("utf-8"))

    intent = stripe.PaymentIntent.create(
        amount=calculate_order_amount(list(data)),
        currency='usd'
    )

    return JsonResponse({
        'clientSecret': intent['client_secret']
    })


def stripe_payment(request):
    if request.GET.get("item_id") is None:
        items = CartItem.objects.filter(user_id=request.user.id)
        total = 0
        data = []

        for i in items:
            unit_price = Item.objects.get(item_id=i.item_id).price
            shipping = Item.objects.get(item_id=i.item_id).shipping
            quantity = i.quantity

            total += quantity * unit_price + shipping

            data.append([Item.objects.get(item_id=i.item_id), i.quantity])


    else:
        if int(request.GET.get("quantity")) < 1:
            return HttpResponseRedirect(f"/stripe/?item_id={request.GET.get('item_id')}&quantity=1")
        elif int(request.GET.get("quantity")) > 10:
            return HttpResponseRedirect(f"/stripe/?item_id={request.GET.get('item_id')}&quantity=10")

        item = Item.objects.get(item_id=request.GET.get("item_id"))
        data = [[item, request.GET.get("quantity")]]
        total = int(request.GET.get("quantity")) * item.price + item.shipping


    return render(request, "shopper/stripe.html", {
        "total": '%.2f' % round(total, 2),
        "data": data
    })


def get_all_cart_item(request):
    if request.GET.get("item_id") == '' or request.GET.get("item_id") == None:
        items = CartItem.objects.filter(user_id=request.user.id)
        data = [[i.item_id, i.quantity] for i in items]

    else:
        item_id = request.GET["item_id"]
        quantity = request.GET["quantity"]
        data = [[item_id, quantity]]

    return JsonResponse({"purchase": data})
