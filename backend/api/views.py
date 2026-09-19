from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db.models import Avg, Max, Sum
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import ChatRoom, Message
from hub.models import Assignment, Material, StudentProgress

from .serializers import (
    AssignmentSerializer,
    MaterialSerializer,
    MessageSerializer,
    ProgressSerializer,
    RoomSerializer,
    UserSerializer,
)

User = get_user_model()


class AuthenticatedOr401(permissions.BasePermission):
    message = "Authentication credentials were not provided."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed({"detail": self.message})
        return True


class ProtectedAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AuthenticatedOr401]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if isinstance(exc, AuthenticationFailed):
            response.status_code = status.HTTP_401_UNAUTHORIZED
        return response


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user = authenticate(
            request,
            username=request.data.get("username"),
            password=request.data.get("password"),
        )
        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        login(request, user)
        return Response({"user": UserSerializer(user).data})


class LogoutView(ProtectedAPIView):
    def post(self, request):
        logout(request)
        return Response({"detail": "Logged out."})


class MeView(ProtectedAPIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class DashboardView(ProtectedAPIView):
    def get(self, request):
        user = request.user
        if user.is_teacher:
            data = {
                "role": "teacher",
                "total_students": User.objects.filter(user_type="student").count(),
                "total_materials": Material.objects.filter(uploaded_by=user).count(),
                "total_assignments": Assignment.objects.filter(created_by=user).count(),
            }
        elif user.is_parent:
            children = User.objects.filter(parent_email=user.email, user_type="student")
            total = sum(Assignment.objects.filter(assigned_to=child).count() for child in children)
            completed = sum(
                StudentProgress.objects.filter(student=child, completed_at__isnull=False).count()
                for child in children
            )
            data = {
                "role": "parent",
                "children": UserSerializer(children, many=True).data,
                "total_assignments": total,
                "completed_assignments": completed,
                "completion_rate": round(completed / total * 100, 1) if total else 0,
            }
        else:
            assignments = Assignment.objects.filter(assigned_to=user, is_active=True).select_related("material")
            progress = StudentProgress.objects.filter(student=user)
            total_assignments = assignments.count()
            completed_assignments = progress.filter(completed_at__isnull=False).count()
            data = {
                "role": "student",
                "total_assignments": total_assignments,
                "completed_assignments": completed_assignments,
                "completion_rate": round((completed_assignments / total_assignments) * 100, 1) if total_assignments else 0,
                "next_assignment": (
                    AssignmentSerializer(assignments.order_by("due_date").first()).data
                    if assignments.exists()
                    else None
                ),
            }
        return Response(data)


class MaterialsView(ProtectedAPIView):
    def get(self, request):
        materials = Material.objects.filter(is_active=True).select_related("subject")
        payload = MaterialSerializer(materials, many=True).data
        return Response({"results": payload, "count": len(payload)})


class AssignmentsView(ProtectedAPIView):
    def get(self, request):
        if request.user.is_student:
            queryset = Assignment.objects.filter(assigned_to=request.user, is_active=True)
        else:
            queryset = Assignment.objects.filter(is_active=True)
        payload = AssignmentSerializer(queryset.select_related("material"), many=True).data
        return Response({"results": payload, "count": len(payload)})


class RoomsView(ProtectedAPIView):
    def get(self, request):
        rooms = ChatRoom.objects.filter(participants=request.user).prefetch_related("participants", "messages")
        payload = RoomSerializer(rooms, many=True).data
        return Response({"results": payload, "count": len(payload)})

    def post(self, request):
        name = str(request.data.get("name", "")).strip()
        if not name:
            return Response({"detail": "A room name is required."}, status=status.HTTP_400_BAD_REQUEST)

        room = ChatRoom.objects.create(name=name, created_by=request.user)
        room.participants.add(request.user)
        return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)


class RoomMessagesView(ProtectedAPIView):
    def get_room(self, request, room_id):
        return ChatRoom.objects.filter(pk=room_id, participants=request.user).first()

    def get(self, request, room_id):
        room = self.get_room(request, room_id)
        if room is None:
            return Response({"detail": "Chat room not found."}, status=status.HTTP_404_NOT_FOUND)

        messages = Message.objects.filter(room=room).select_related("sender").order_by("timestamp")
        payload = MessageSerializer(messages, many=True).data
        return Response({"results": payload, "count": len(payload)})

    def post(self, request, room_id):
        room = self.get_room(request, room_id)
        if room is None:
            return Response({"detail": "Chat room not found."}, status=status.HTTP_404_NOT_FOUND)

        content = str(request.data.get("content", "")).strip()
        if not content:
            return Response({"detail": "Message cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        message = Message.objects.create(room=room, sender=request.user, content=content)
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)


class ProgressView(ProtectedAPIView):
    def get(self, request):
        records = StudentProgress.objects.filter(student=request.user).select_related("material")
        scored = records.filter(score__isnull=False)
        return Response(
            {
                "records": ProgressSerializer(records, many=True).data,
                "total_count": records.count(),
                "completed_count": records.filter(status="completed").count(),
                "in_progress_count": records.filter(status="in_progress").count(),
                "overall_completion": (
                    round(records.filter(status="completed").count() / records.count() * 100, 1)
                    if records.exists()
                    else 0
                ),
                "average_score": scored.aggregate(value=Avg("score"))["value"] or 0,
                "best_score": scored.aggregate(value=Max("score"))["value"],
                "total_study_time": records.aggregate(value=Sum("time_spent_minutes"))["value"] or 0,
            }
        )
