from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse

# Create your views here.

def register(request):
    if request.method == "POST":
        fname = request.POST["first-name"]
        lname = request.POST["last-name"]
        email = request.POST["email"]
        country_code = request.POST["country-code"]
        phone = request.POST["phone-number"]
        password = request.POST["password"]
        role = request.POST["role"]

        User.objects.create_user(username=email, email=email, first_name=fname, last_name=lname, password=password).save()

        return HttpResponse("registered successfully")

    else:
        return render(request, "authentication/register.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(username=email, password=password)

        if user is not None:
            login(request, user)
            return HttpResponse("logged in successfully")
        else:
            return HttpResponse("You entered wrong credentials.")

    else:
        return render(request, "authentication/login.html")


def logout_view(request):
    logout(request)
    return HttpResponse("logged out successfully")
