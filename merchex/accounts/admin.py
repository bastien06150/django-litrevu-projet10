from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import UserFollows


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass


@admin.register(UserFollows)
class UserFollowsAdmin(admin.ModelAdmin):
    list_display = ("user", "followed_user")
