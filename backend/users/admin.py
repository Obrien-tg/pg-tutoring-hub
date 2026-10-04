from django.contrib import admin

from .models import CustomUser, FirebaseToken


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "user_type",
        "is_verified",
        "is_active",
        "date_joined",
    )
    list_filter = ("user_type", "is_verified", "is_active")
    search_fields = ("username", "email", "first_name", "last_name", "parent_email")


@admin.register(FirebaseToken)
class FirebaseTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "device_info", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("user__username", "user__email", "token")
