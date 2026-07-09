from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "nama", "role", "is_active", "is_superuser")
    list_filter = ("role", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Info Tambahan", {"fields": ("role", "nama")}),
    )
