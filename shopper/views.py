from django.shortcuts import render
from seller.models import Item, ItemPicture
# from django.http import HttpRequest

# Create your views here.
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
        return render(request, "shopper/index.html")


def view_item(request, item_id):
    item = Item.objects.get(item_id=item_id)
    images = ItemPicture.objects.filter(item_id=item_id)

    print(images)
    print(images[1:])

    return render(request, "shopper/view-item.html", {
        "item": item,
        "image0": images[0],
        "images": images[1:]
    })

