from django.contrib import admin
from .models import EmailOTP, User

# Register your models here.

admin.site.register(User)
admin.site.register(EmailOTP)
