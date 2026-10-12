from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Avg, Count, Max, Prefetch, Sum
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.throttling import AnonRateThrottle
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import ChatRoom, Message
from hub.models import Assignment, AssignmentSubmission, Material, StudentProgress
from users.firebase_utils import send_submission_notification
from users import firebase_utils
from users.models import ParentChildLink

from dashboard.services import build_student_dashboard

from .serializers import (
    AssignmentSerializer,
    AssignmentDetailSerializer,
    AssignmentSubmissionSerializer,
    MaterialSerializer,
    MessageSerializer,
    ParentChildListSerializer,
    ProgressSerializer,
    RoomSerializer,
    UserSerializer,
)
from .permissions import IsParentUser, IsStudentUser

User = get_user_model()


@ensure_csrf_cookie
def csrf_view(request):
    return JsonResponse({"csrfToken": get_token(request)})


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


class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        email = str(request.data.get("email", "")).strip()
        if email:
            # NOTE: Django default reset email contains a backend template link.
            # SPA "Forgot Password" UI and custom email templates are a non-goal for P1.
            form = PasswordResetForm({"email": email})
            if form.is_valid():
                form.save(
                    use_https=request.is_secure(),
                    request=request,
                    from_email=None,
                )
        return Response(
            {
                "detail": (
                    "If an account with this email exists, a password reset link "
                    "has been sent."
                )
            }
        )


class ParentChildrenListView(ProtectedAPIView):
    permission_classes = [AuthenticatedOr401, IsParentUser]

    def get(self, request):
        links = (
            ParentChildLink.objects.filter(parent=request.user, is_active=True)
            .select_related("student")
        )
        return Response(ParentChildListSerializer(links, many=True).data)


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
            links = (
                ParentChildLink.objects.filter(parent=user, is_active=True)
                .select_related("student")
            )
            children = []
            total = completed = 0
            for link in links:
                child = link.student
                assignments = Assignment.objects.filter(
                    assigned_to=child,
                    is_active=True,
                )
                child_total = assignments.count()
                child_completed = StudentProgress.objects.filter(
                    student=child,
                    assignment__in=assignments,
                    completed_at__isnull=False,
                ).count()
                recent_grades = AssignmentSubmission.objects.filter(
                    student=child,
                    status="graded",
                ).select_related("assignment").order_by("-graded_at", "-pk")[:5]
                children.append(
                    {
                        "id": child.id,
                        "student_name": child.full_name,
                        "student_email": child.email or "",
                        "total_assignments": child_total,
                        "completed_assignments": child_completed,
                        "completion_rate": (
                            round(child_completed / child_total * 100, 1)
                            if child_total
                            else 0
                        ),
                        "recent_grades": [
                            {
                                "assignment_title": submission.assignment.title,
                                "grade": submission.grade,
                                "numeric_score": submission.numeric_score,
                            }
                            for submission in recent_grades
                        ],
                    }
                )
                total += child_total
                completed += child_completed
            data = {
                "role": "parent",
                "children": children,
                "total_assignments": total,
                "completed_assignments": completed,
                "completion_rate": round(completed / total * 100, 1) if total else 0,
            }
        else:
            dashboard = build_student_dashboard(user)
            data = {
                "role": "student",
                "total_assignments": dashboard["total_assignments"],
                "completed_assignments": dashboard["completed_assignments"],
                "completion_rate": round(dashboard["completion_rate"], 1),
                "next_assignment": (
                    AssignmentSerializer(dashboard["next_assignment"]).data
                    if dashboard["next_assignment"]
                    else None
                ),
                "graded_submissions": AssignmentSubmissionSerializer(
                    dashboard["graded_submissions"],
                    many=True,
                ).data,
                "subject_mastery": dashboard["subject_mastery"],
                "weekly_effort": dashboard["weekly_effort"],
            }
        return Response(data)


class MaterialsView(ProtectedAPIView):
    def get(self, request):
        materials = Material.objects.filter(is_active=True).select_related("subject")
        payload = MaterialSerializer(materials, many=True).data
        return Response({"results": payload, "count": len(payload)})


class MaterialDetailView(ProtectedAPIView):
    def get(self, request, material_id):
        material = (
            Material.objects.filter(pk=material_id, is_active=True)
            .select_related("subject")
            .first()
        )
        if material is None:
            return Response(
                {"detail": "Material not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(MaterialSerializer(material).data)


class AssignmentsView(ProtectedAPIView):
    def get(self, request):
        if request.user.is_student:
            queryset = Assignment.objects.filter(assigned_to=request.user, is_active=True)
        else:
            queryset = Assignment.objects.filter(is_active=True)
        payload = AssignmentSerializer(queryset.select_related("material"), many=True).data
        return Response({"results": payload, "count": len(payload)})


class AssignmentDetailView(ProtectedAPIView):
    def get(self, request, assignment_id):
        assignment = Assignment.objects.prefetch_related("submissions").filter(
            pk=assignment_id, is_active=True
        ).first()
        if assignment is None:
            return Response({"detail": "Assignment not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.is_student and not assignment.assigned_to.filter(pk=request.user.pk).exists():
            return Response({"detail": "Assignment not found."}, status=status.HTTP_404_NOT_FOUND)
        if not request.user.is_student and assignment.created_by_id != request.user.id:
            return Response({"detail": "Assignment not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(AssignmentDetailSerializer(assignment, context={"request": request}).data)


class AssignmentSubmissionView(ProtectedAPIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, assignment_id):
        assignment = Assignment.objects.filter(pk=assignment_id).first()
        if assignment is None:
            return Response(
                {"detail": "Assignment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.is_student or not assignment.assigned_to.filter(
            pk=request.user.pk
        ).exists():
            return Response(
                {"detail": "You are not authorized to submit this assignment."},
                status=status.HTTP_403_FORBIDDEN,
            )

        submission_text = str(request.data.get("submission_text", "")).strip()
        submission_notes = str(request.data.get("submission_notes", "")).strip()
        submission_file = request.FILES.get("submission_file")
        if submission_file and submission_file.size > 10 * 1024 * 1024:
            return Response(
                {"detail": "Submission files must be 10 MB or smaller."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not submission_text and not submission_file:
            return Response(
                {"detail": "Provide submission text or a file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            submission = (
                AssignmentSubmission.objects.select_for_update()
                .filter(assignment=assignment, student=request.user)
                .first()
            )
            if submission is None:
                submission = AssignmentSubmission(
                    assignment=assignment,
                    student=request.user,
                )

            submission.submission_text = submission_text
            submission.submission_notes = submission_notes
            if submission_file:
                submission.submission_file = submission_file
            submission.status = "submitted"
            try:
                submission.full_clean()
                submission.save()
            except ValidationError as exc:
                return Response(
                    {"detail": exc.message_dict if hasattr(exc, "message_dict") else exc.messages},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        send_submission_notification(submission)
        return Response(
            AssignmentSubmissionSerializer(submission).data,
            status=status.HTTP_201_CREATED,
        )


class GradeSubmissionView(ProtectedAPIView):
    """Allow the teacher who owns an assignment to grade its submission."""

    def post(self, request, submission_id):
        submission = (
            AssignmentSubmission.objects.select_related(
                "assignment", "student", "assignment__created_by"
            )
            .filter(pk=submission_id)
            .first()
        )
        if submission is None:
            return Response(
                {"detail": "Submission not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.is_teacher:
            return Response(
                {"detail": "Only teachers can grade submissions."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if submission.assignment.created_by_id != request.user.id:
            return Response(
                {"detail": "You are not authorized to grade this submission."},
                status=status.HTTP_403_FORBIDDEN,
            )

        action = str(request.data.get("action", "")).strip().lower()
        if action not in {"grade", "revision"}:
            return Response(
                {"detail": "Action must be either 'grade' or 'revision'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                submission = (
                    AssignmentSubmission.objects.select_for_update()
                    .select_related("assignment", "student")
                    .get(pk=submission_id)
                )
                if action == "grade":
                    if "grade" in request.data:
                        submission.grade = str(request.data.get("grade") or "").strip()
                    if "numeric_score" in request.data:
                        raw_score = request.data.get("numeric_score")
                        submission.numeric_score = (
                            None if raw_score in ("", None) else int(raw_score)
                        )
                        if "grade" not in request.data:
                            submission.grade = ""
                    if "teacher_feedback" in request.data:
                        submission.teacher_feedback = str(
                            request.data.get("teacher_feedback") or ""
                        ).strip()
                    if submission.grade == "" and submission.numeric_score is None:
                        return Response(
                            {"detail": "Provide a grade or numeric_score."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    submission.revision_requested = False
                    submission.revision_notes = ""
                    submission.graded_by = request.user
                    submission.status = "graded"
                    submission.graded_at = timezone.now()
                else:
                    revision_notes = str(
                        request.data.get("revision_notes") or ""
                    ).strip()
                    if not revision_notes:
                        return Response(
                            {"detail": "Revision notes are required."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    submission.revision_requested = True
                    submission.revision_notes = revision_notes
                    submission.status = "returned"
                    submission.graded_by = request.user
                    if "teacher_feedback" in request.data:
                        submission.teacher_feedback = str(
                            request.data.get("teacher_feedback") or ""
                        ).strip()

                submission.full_clean()
                submission.save()
        except (TypeError, ValueError):
            return Response(
                {"detail": "numeric_score must be a whole number."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as exc:
            return Response(
                {
                    "detail": (
                        exc.message_dict
                        if hasattr(exc, "message_dict")
                        else exc.messages
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action == "grade":
            firebase_utils.send_notification_to_user(
                submission.student,
                {
                    "title": "Assignment Graded",
                    "body": f"Your assignment '{submission.assignment.title}' has been graded",
                    "icon": "/static/img/assignment-icon.png",
                },
                {
                    "type": "assignment",
                    "assignment_id": str(submission.assignment_id),
                    "submission_id": str(submission.id),
                    "action": "graded",
                },
            )
        else:
            firebase_utils.send_notification_to_user(
                submission.student,
                {
                    "title": "Revision Requested",
                    "body": f"Revision requested for '{submission.assignment.title}'",
                    "icon": "/static/img/assignment-icon.png",
                },
                {
                    "type": "assignment",
                    "assignment_id": str(submission.assignment_id),
                    "submission_id": str(submission.id),
                    "action": "revision",
                },
            )

        return Response(AssignmentSubmissionSerializer(submission).data)


class RoomsView(ProtectedAPIView):
    def get(self, request):
        latest_messages = Message.objects.select_related("sender").order_by(
            "-timestamp", "-pk"
        )[:1]
        rooms = ChatRoom.objects.filter(
            participants=request.user
        ).prefetch_related(
            "participants",
            Prefetch(
                "messages",
                queryset=latest_messages,
                to_attr="prefetched_latest_messages",
            ),
        )
        payload = RoomSerializer(rooms, many=True).data
        return Response({"results": payload, "count": len(payload)})

    def post(self, request):
        name = str(request.data.get("name", "")).strip()
        if not name:
            return Response({"detail": "A room name is required."}, status=status.HTTP_400_BAD_REQUEST)

        room = ChatRoom.objects.create(name=name, created_by=request.user)
        room.participants.add(request.user)
        return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)


class TeacherChatView(ProtectedAPIView):
    def post(self, request):
        if request.user.user_type != "student":
            return Response(
                {"detail": "Only students can open a teacher chat."},
                status=status.HTTP_403_FORBIDDEN,
            )

        teacher = (
            User.objects.filter(user_type="teacher", is_active=True)
            .order_by("id")
            .first()
        )
        if teacher is None:
            return Response(
                {"detail": "No active teacher is available."},
                status=status.HTTP_404_NOT_FOUND,
            )

        with transaction.atomic():
            student = User.objects.select_for_update().get(pk=request.user.pk)
            candidate_room_ids = (
                ChatRoom.objects.filter(
                    is_group_chat=False,
                    participants=student,
                )
                .filter(participants=teacher)
                .values("pk")
            )
            room = (
                ChatRoom.objects.filter(pk__in=candidate_room_ids)
                .annotate(
                    participant_count=Count("participants", distinct=True)
                )
                .filter(participant_count=2)
                .first()
            )
            created = room is None
            if created:
                room = ChatRoom.objects.create(
                    name=f"Chat with {teacher.get_full_name() or teacher.username}",
                    is_group_chat=False,
                    created_by=student,
                )
                room.participants.add(student, teacher)

        return Response(
            RoomSerializer(room).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


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
    permission_classes = [AuthenticatedOr401, IsStudentUser]

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


class ParentChildProgressView(ProtectedAPIView):
    permission_classes = [AuthenticatedOr401, IsParentUser]

    def get(self, request, student_id):
        linked = ParentChildLink.objects.filter(
           parent=request.user,
           student_id=student_id,
           is_active=True,
        ).exists()
        if not linked:
           return Response(
               {"detail": "Student not found."},
               status=status.HTTP_404_NOT_FOUND,
           )
        records = StudentProgress.objects.filter(
           student_id=student_id,
        ).select_related("material")
        return Response(ProgressSerializer(records, many=True).data)
