from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.http import HttpRequest

admin.site.register(get_user_model())
