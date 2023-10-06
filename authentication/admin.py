from django.contrib import admin
from .models import Profile

# Register your models here.
admin.site.register(Profile)
admin.site.register(TWOFAVerified)
admin.site.register(TwoFAToken)
