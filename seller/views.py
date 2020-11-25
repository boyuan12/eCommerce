from django.shortcuts import render

# Create your views here.
def index():
    pass


def create_shop(request):
    if request.method == "POST":
        pass

    else:
        return render(request, "seller/create-shop.html")
