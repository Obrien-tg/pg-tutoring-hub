from django.conf import settings
from django.db import models


class ChatRoom(models.Model):
    """Chat rooms for communication between teacher and students/parents"""

    name = models.CharField(max_length=200)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="chat_rooms"
    )

    # Room metadata
    is_group_chat = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_rooms"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def latest_message(self):
        return self.messages.first()


class Message(models.Model):
    """Individual messages in chat rooms"""

    MESSAGE_TYPES = (
        ("text", "Text"),
        ("file", "File"),
        ("image", "Image"),
        ("assignment", "Assignment"),
    )

    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Message content
    message_type = models.CharField(
        max_length=20, choices=MESSAGE_TYPES, default="text"
    )
    content = models.TextField(blank=True)
    file = models.FileField(upload_to="chat_files/", blank=True, null=True)

    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..."


class MessageReadStatus(models.Model):
    """Track which users have read which messages"""

    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="read_status"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("message", "user")
