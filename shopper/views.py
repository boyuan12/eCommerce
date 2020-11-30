import datetime
from django.shortcuts import render
from seller.models import Item, ItemPicture
from .models import PageView
# from django.http import HttpRequest

# Create your views here.
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

        try:
            PageView.objects.filter(timestamp__hour=str(current_hour-1)).delete()
        except:
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

    PageView(item_id=item_id).save()

    return render(request, "shopper/view-item.html", {
        "item": item,
        "image0": images[0],
        "images": images[1:]
    })

