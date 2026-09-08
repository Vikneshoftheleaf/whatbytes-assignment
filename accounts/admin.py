from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "name", "is_staff", "is_active")
    ordering = ("email",)
    search_fields = ("email", "name")
    fieldsets = ((None, {"fields": ("email", "password")}), ("Personal info", {"fields": ("name",)}), ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}))
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "name", "password1", "password2", "is_staff", "is_active")} ),)
