from django.http.request import HttpRequest
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from twilio.rest import Client
from .models import AuthorizedDevice, Profile, TwoFAToken, TWOFAVerified
from helpers import random_str
import os

# Create your views here.
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

c = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

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
        u = User.objects.get(username=email)
        if role == "shopper":
            role = 0
        else:
            role = 1
        Profile(user_id=u.id, role=role).save()

        code = random_str()
        c.messages.create(from_='+19162800623', body='TWOFA Code: ' + code, to='+' + country_code + phone)
        TwoFAToken(user_id=u.id, code=code, phone='+' + country_code + phone).save()

        return HttpResponse("registered successfully, please check your phone to complete 2FA")

    else:
        return render(request, "authentication/register.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        auth_device_id = request.POST["auth-device-id"]

        user = authenticate(username=email, password=password)

        if user is not None:
            try:
                TWOFAVerified.objects.get(user_id=user.id)
                try:
                    AuthorizedDevice.objects.get(uuid=auth_device_id)
                except:
                    request.session["2fa_user_id"] = user.id
                    return HttpResponseRedirect("/auth/2fa/")
                login(request, user)
                p = Profile.objects.get(user_id=user.id)
                if p.role == 0:
                    return HttpResponseRedirect("/")
                else:
                    return HttpResponseRedirect("/seller/")
                # return HttpResponse("logged in successfully")
            except:
                return HttpResponse("Please complete initial 2FA first.")

        else:
            return HttpResponse("You entered wrong credentials.")

    else:
        if request.session.get("deviceid") != None:
            deviceId = request.session.get("deviceid")
            print(deviceId)
            request.session["deviceid"] = None
            return render(request, "authentication/login.html", {
                "deviceid": deviceId,
                "verified": True
            })
        return render(request, "authentication/login.html")


def logout_view(request):
    logout(request)
    return HttpResponse("logged out successfully")


def complete_2fa(request):
    if request.method == "POST":
        code = request.POST["code"]
        try:
            t = TwoFAToken.objects.get(code=code)
        except:
            return HttpResponse("Invalid code")

        user_id = t.user_id
        phone = t.phone
        t.delete()

        TWOFAVerified(user_id=user_id, phone=phone).save()

        return HttpResponse("2FA completed, please login")
    else:
        return render(request, "authentication/2fa.html")


def twofa_verify(request: HttpRequest):
    if request.method == "POST":
        code = request.POST["code"]
        try:
            t = TwoFAToken.objects.get(code=code)
        except:
            return HttpResponse("Invalid code")
        user = User.objects.get(id=t.user_id)
        AuthorizedDevice(user_id=user.id).save()
        a = AuthorizedDevice.objects.filter(user_id=user.id)[::-1][0]
        login(request, user)
        request.session["deviceid"] = str(a.uuid)
        return HttpResponseRedirect("/auth/login/")


    else:
        code = random_str()
        TwoFAToken(user_id=request.session.get("2fa_user_id"), code=code).save()
        phone = TWOFAVerified.objects.get(user_id=request.session.get("2fa_user_id")).phone
        c.messages.create(from_='+19162800623', body='TWOFA Code: ' + code, to=phone)
        return render(request, "authentication/2fa.html")