from django.contrib import admin

from .models import ChatRoom, Message, MessageReadStatus


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "is_group_chat", "created_at")
    list_filter = ("is_group_chat", "created_at")
    search_fields = ("name", "created_by__username", "participants__username")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("room", "sender", "message_type", "is_read", "timestamp")
    list_filter = ("message_type", "is_read", "timestamp")
    search_fields = ("content", "sender__username", "room__name")


@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    list_display = ("message", "user", "read_at")
    list_filter = ("read_at",)
    search_fields = ("user__username", "message__content")
