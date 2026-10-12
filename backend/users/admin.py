from django.contrib import admin

from .models import CustomUser, FirebaseToken, ParentChildLink


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


@admin.register(ParentChildLink)
class ParentChildLinkAdmin(admin.ModelAdmin):
    list_display = ("parent", "student", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = (
        "parent__email",
        "parent__username",
        "student__email",
        "student__username",
    )
    raw_id_fields = ("parent", "student")
    date_hierarchy = "created_at"
