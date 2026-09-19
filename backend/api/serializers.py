from rest_framework import serializers

from chat.models import ChatRoom, Message
from hub.models import Assignment, Material, StudentProgress


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    user_type = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)


class MaterialSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    file_url = serializers.FileField(source="file", read_only=True)

    class Meta:
        model = Material
        fields = (
            "id", "title", "description", "material_type", "subject", "subject_name",
            "difficulty_level", "grade_level", "estimated_time", "tags",
            "external_link", "file_url", "created_at",
        )


class AssignmentSerializer(serializers.ModelSerializer):
    material_title = serializers.CharField(source="material.title", read_only=True)
    assigned_to = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Assignment
        fields = (
            "id", "title", "description", "material", "material_title", "assigned_to",
            "due_date", "priority", "max_score", "instructions",
            "submission_format", "is_active",
        )


class ProgressSerializer(serializers.ModelSerializer):
    material_title = serializers.CharField(source="material.title", read_only=True)

    class Meta:
        model = StudentProgress
        fields = (
            "id", "material", "material_title", "assignment", "status", "score",
            "completion_percentage", "time_spent_minutes", "started_at",
            "completed_at", "teacher_feedback",
        )


class RoomSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    latest_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ("id", "name", "participants", "is_group_chat", "created_by", "created_at", "latest_message")

    def get_latest_message(self, obj):
        message = obj.latest_message
        return MessageSerializer(message).data if message else None


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = Message
        fields = ("id", "room", "sender", "sender_username", "message_type", "content", "file", "timestamp", "is_read")
        read_only_fields = ("sender", "room")
