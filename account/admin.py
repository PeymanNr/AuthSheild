from django.contrib import admin
from django.contrib.admin import register
from account.models import User


@register(User)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'phone_number', 'first_name',
                          'last_name', 'password')