from unittest.mock import patch
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from chat.models import ChatRoom, Message
from hub.models import Assignment, AssignmentSubmission, Material, Subject
from users.models import ParentChildLink

User = get_user_model()


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "api-email-tests",
        }
    }
)
class EmailApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear()
        self.user = User.objects.create_user(
            username="reset_user",
            email="reset@example.com",
            password="test-password",
            user_type="student",
        )

    def test_password_reset_existing_user_sends_email(self):
        response = self.client.post(
            "/api/auth/password/reset/",
            {"email": self.user.email},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_unknown_user_does_not_send_email(self):
        response = self.client.post(
            "/api/auth/password/reset/",
            {"email": "missing@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_is_rate_limited(self):
        responses = [
            self.client.post(
                "/api/auth/password/reset/",
                {"email": self.user.email},
                format="json",
            )
            for _ in range(6)
        ]

        self.assertEqual([response.status_code for response in responses[:5]], [200] * 5)
        self.assertEqual(responses[5].status_code, 429)

    def test_media_root_is_writable(self):
        settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
        test_file = settings.MEDIA_ROOT / "write_test.txt"
        try:
            test_file.write_text("ok")
            self.assertTrue(test_file.exists())
        finally:
            test_file.unlink(missing_ok=True)


class ParentDashboardApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.parent = User.objects.create_user(
            username="dashboard_parent",
            email="dashboard-parent@example.com",
            password="test-password",
            user_type="parent",
        )
        self.student = User.objects.create_user(
            username="dashboard_student",
            email="dashboard-student@example.com",
            password="test-password",
            user_type="student",
            grade_level="5",
            parent_email="dashboard-parent@example.com",
        )
        self.teacher = User.objects.create_user(
            username="dashboard_teacher",
            email="dashboard-teacher@example.com",
            password="test-password",
            user_type="teacher",
        )

    def test_parent_dashboard_uses_linked_children_and_is_aggregated(self):
        ParentChildLink.objects.create(parent=self.parent, student=self.student)
        subject = Subject.objects.create(name="Dashboard Maths")
        material = Material.objects.create(
            title="Fractions",
            description="Practice",
            material_type="worksheet",
            subject=subject,
            difficulty_level="beginner",
            external_link="https://example.com/fractions",
            grade_level="5",
            estimated_time=30,
            uploaded_by=self.teacher,
        )
        assignment = Assignment.objects.create(
            title="Fractions task",
            description="Complete the task",
            material=material,
            due_date=timezone.now() + timedelta(days=2),
            created_by=self.teacher,
        )
        assignment.assigned_to.add(self.student)

        self.client.force_authenticate(self.parent)
        response = self.client.get("/api/dashboard/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["children"][0]["id"], self.student.id)
        self.assertEqual(payload["children"][0]["total_assignments"], 1)
        self.assertEqual(payload["total_assignments"], 1)
        self.assertEqual(payload["completed_assignments"], 0)

    def test_parent_without_links_has_empty_dashboard(self):
        self.client.force_authenticate(self.parent)

        payload = self.client.get("/api/dashboard/").json()

        self.assertEqual(payload["children"], [])
        self.assertEqual(payload["completion_rate"], 0)

    def test_non_parent_cannot_read_parent_dashboard_or_progress(self):
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get("/api/dashboard/").status_code, 200)
        self.assertEqual(self.client.get("/api/parent/children/").status_code, 403)
        self.assertEqual(self.client.get("/api/progress/").status_code, 200)

        self.client.force_authenticate(self.teacher)
        self.assertEqual(self.client.get("/api/parent/children/").status_code, 403)
        self.assertEqual(self.client.get("/api/progress/").status_code, 403)


class ApiAuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="api_student",
            password="test-password",
            email="api@example.com",
            user_type="student",
            grade_level="5",
            parent_email="parent@example.com",
        )

    def test_protected_endpoints_return_json_401_when_logged_out(self):
        for path in ("/api/auth/me/", "/api/dashboard/", "/api/materials/", "/api/assignments/", "/api/progress/"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 401, path)
            self.assertEqual(response["Content-Type"], "application/json", path)
            self.assertIn("detail", response.json())

    def test_logged_in_user_can_read_core_endpoints(self):
        self.client.force_authenticate(self.user)
        for path in ("/api/auth/me/", "/api/dashboard/", "/api/materials/", "/api/assignments/", "/api/progress/"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertIsInstance(response.json(), dict, path)

    def test_login_and_logout(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "api_student", "password": "test-password"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["username"], "api_student")
        self.assertEqual(self.client.post("/api/auth/logout/", format="json").status_code, 200)


class MaterialApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username="materials_teacher",
            email="materials-teacher@example.com",
            password="test-password",
            user_type="teacher",
        )
        self.student = User.objects.create_user(
            username="materials_student",
            email="materials-student@example.com",
            password="test-password",
            user_type="student",
            grade_level="5",
            parent_email="parent@example.com",
        )
        subject = Subject.objects.create(name="Materials Mathematics")
        self.material = Material.objects.create(
            title="Fractions practice",
            description="Build confidence with fractions.",
            material_type="worksheet",
            subject=subject,
            difficulty_level="beginner",
            grade_level="5",
            estimated_time=20,
            uploaded_by=self.teacher,
            external_link="https://example.com/fractions",
        )
        self.file_material = Material.objects.create(
            title="Fractions worksheet file",
            description="Practise with a downloadable worksheet.",
            material_type="worksheet",
            subject=subject,
            difficulty_level="beginner",
            grade_level="5",
            estimated_time=20,
            uploaded_by=self.teacher,
            file=SimpleUploadedFile("fractions.pdf", b"worksheet"),
        )
        self.inactive_material = Material.objects.create(
            title="Retired worksheet",
            description="No longer available.",
            material_type="worksheet",
            subject=subject,
            difficulty_level="beginner",
            grade_level="5",
            estimated_time=15,
            uploaded_by=self.teacher,
            external_link="https://example.com/retired",
            is_active=False,
        )
        self.client.force_authenticate(self.student)

    def test_material_list_returns_active_materials(self):
        response = self.client.get("/api/materials/")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()["results"], list)
        self.assertEqual(response.json()["count"], 2)
        result_ids = {item["id"] for item in response.json()["results"]}
        self.assertEqual(result_ids, {self.material.pk, self.file_material.pk})

    def test_material_detail_returns_links_and_matching_fields(self):
        response = self.client.get(f"/api/materials/{self.material.pk}/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["title"], self.material.title)
        self.assertEqual(payload["external_link"], self.material.external_link)
        self.assertIsNone(payload["file_url"])

        file_response = self.client.get(f"/api/materials/{self.file_material.pk}/")
        self.assertEqual(file_response.status_code, 200)
        self.assertTrue(file_response.json()["file_url"])
        self.assertEqual(file_response.json()["external_link"], "")

    def test_inactive_or_missing_material_returns_json_404(self):
        for material_id in (self.inactive_material.pk, 99999):
            response = self.client.get(f"/api/materials/{material_id}/")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {"detail": "Material not found."})

    def test_material_list_requires_authentication(self):
        self.client.force_authenticate(None)

        response = self.client.get("/api/materials/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("detail", response.json())


class AssignmentSubmissionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username="api_teacher",
            email="api-teacher@example.com",
            password="test-password",
            user_type="teacher",
        )
        self.student = User.objects.create_user(
            username="submission_student",
            email="submission-student@example.com",
            password="test-password",
            user_type="student",
            grade_level="5",
            parent_email="parent@example.com",
        )
        self.other_student = User.objects.create_user(
            username="other_submission_student",
            email="other-submission-student@example.com",
            password="test-password",
            user_type="student",
            grade_level="5",
            parent_email="other-parent@example.com",
        )
        subject = Subject.objects.create(name="API Mathematics")
        material = Material.objects.create(
            title="API Worksheet",
            description="Worksheet for API submission tests.",
            material_type="worksheet",
            subject=subject,
            difficulty_level="beginner",
            grade_level="5",
            estimated_time=30,
            uploaded_by=self.teacher,
            external_link="https://example.com/api-worksheet",
        )
        self.assignment = Assignment.objects.create(
            title="Submit this worksheet",
            description="Complete the worksheet.",
            material=material,
            due_date=timezone.now() + timezone.timedelta(days=2),
            created_by=self.teacher,
        )
        self.assignment.assigned_to.add(self.student)

    @patch("api.views.send_submission_notification")
    def test_student_can_submit_multipart_file(self, notify):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            f"/api/assignments/{self.assignment.pk}/submissions/",
            {
                "submission_text": "My completed work",
                "submission_notes": "Please check question 4.",
                "submission_file": SimpleUploadedFile(
                    "work.pdf",
                    b"%PDF-1.4 test",
                    content_type="application/pdf",
                ),
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        submission = AssignmentSubmission.objects.get(
            assignment=self.assignment,
            student=self.student,
        )
        self.assertEqual(submission.status, "submitted")
        self.assertEqual(submission.submission_text, "My completed work")
        self.assertTrue(submission.submission_file)
        notify.assert_called_once_with(submission)

    @patch("api.views.send_submission_notification")
    def test_resubmission_updates_existing_submission(self, notify):
        existing = AssignmentSubmission.objects.create(
            assignment=self.assignment,
            student=self.student,
            submission_text="First attempt",
        )
        self.client.force_authenticate(self.student)

        response = self.client.post(
            f"/api/assignments/{self.assignment.pk}/submissions/",
            {"submission_text": "Revised attempt"},
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        existing.refresh_from_db()
        self.assertEqual(existing.submission_text, "Revised attempt")
        self.assertEqual(
            AssignmentSubmission.objects.filter(
                assignment=self.assignment,
                student=self.student,
            ).count(),
            1,
        )
        notify.assert_called_once_with(existing)

    def test_submission_requires_text_or_file(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            f"/api/assignments/{self.assignment.pk}/submissions/",
            {"submission_notes": "Nothing attached yet"},
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())
        self.assertFalse(AssignmentSubmission.objects.exists())

    def test_unassigned_student_cannot_submit(self):
        self.client.force_authenticate(self.other_student)
        response = self.client.post(
            f"/api/assignments/{self.assignment.pk}/submissions/",
            {"submission_text": "Unauthorized work"},
            format="multipart",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(AssignmentSubmission.objects.exists())

    def test_invalid_file_extension_is_rejected(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            f"/api/assignments/{self.assignment.pk}/submissions/",
            {
                "submission_file": SimpleUploadedFile(
                    "work.exe",
                    b"not allowed",
                    content_type="application/octet-stream",
                )
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(AssignmentSubmission.objects.exists())

    def test_submission_file_over_10mb_is_rejected(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            f"/api/assignments/{self.assignment.pk}/submissions/",
            {
                "submission_file": SimpleUploadedFile(
                    "work.pdf",
                    b"x" * (10 * 1024 * 1024 + 1),
                    content_type="application/pdf",
                )
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "Submission files must be 10 MB or smaller.",
        )
        self.assertFalse(AssignmentSubmission.objects.exists())

    def test_assignment_detail_includes_student_submission(self):
        submission = AssignmentSubmission.objects.create(
            assignment=self.assignment,
            student=self.student,
            submission_text="My answer",
        )
        self.client.force_authenticate(self.student)
        response = self.client.get(f"/api/assignments/{self.assignment.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.assignment.pk)
        self.assertEqual(response.json()["submission"]["id"], submission.pk)
        self.assertEqual(response.json()["submission"]["submission_text"], "My answer")

    def test_assignment_detail_requires_assignment_access(self):
        self.client.force_authenticate(self.other_student)
        response = self.client.get(f"/api/assignments/{self.assignment.pk}/")
        self.assertEqual(response.status_code, 404)

    def test_protected_assignment_routes_return_json_401(self):
        for path in (
            "/api/assignments/",
            f"/api/assignments/{self.assignment.pk}/",
        ):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 401, path)
            self.assertIn("detail", response.json())


class SubmissionGradingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username="grading_teacher",
            email="grading-teacher@example.com",
            password="grading-password",
            user_type="teacher",
        )
        self.other_teacher = User.objects.create_user(
            username="other_grading_teacher",
            email="other-grading-teacher@example.com",
            password="grading-password",
            user_type="teacher",
        )
        self.student = User.objects.create_user(
            username="grading_student",
            email="grading-student@example.com",
            password="grading-password",
            user_type="student",
            grade_level="5",
            parent_email="grading-parent@example.com",
        )
        subject = Subject.objects.create(name="Grading Mathematics")
        material = Material.objects.create(
            title="Grading worksheet",
            description="Worksheet for grading tests.",
            material_type="worksheet",
            subject=subject,
            difficulty_level="beginner",
            grade_level="5",
            estimated_time=30,
            uploaded_by=self.teacher,
            external_link="https://example.com/grading",
        )
        assignment = Assignment.objects.create(
            title="Grade this worksheet",
            description="Complete the worksheet.",
            material=material,
            due_date=timezone.now() + timezone.timedelta(days=2),
            created_by=self.teacher,
        )
        assignment.assigned_to.add(self.student)
        self.submission = AssignmentSubmission.objects.create(
            assignment=assignment,
            student=self.student,
            submission_text="My completed answers",
        )

    @patch("api.views.firebase_utils.send_notification_to_user")
    def test_owner_can_grade_score_only_and_auto_fill_letter(self, notify):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            f"/api/submissions/{self.submission.pk}/grade/",
            {"action": "grade", "numeric_score": 85},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.submission.refresh_from_db()
        self.assertEqual(response.json()["grade"], "B")
        self.assertEqual(self.submission.status, "graded")
        self.assertEqual(self.submission.graded_by_id, self.teacher.pk)
        self.assertFalse(self.submission.revision_requested)
        self.assertIsNotNone(self.submission.graded_at)
        notify.assert_called_once()
        self.assertEqual(notify.call_args.args[0], self.student)

    @patch("api.views.firebase_utils.send_notification_to_user")
    def test_owner_can_request_revision_with_notes(self, notify):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            f"/api/submissions/{self.submission.pk}/grade/",
            {"action": "revision", "revision_notes": "Please show your working."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, "returned")
        self.assertTrue(self.submission.revision_requested)
        self.assertEqual(self.submission.revision_notes, "Please show your working.")
        notify.assert_called_once()

    def test_revision_requires_notes_and_missing_submission_is_404(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            f"/api/submissions/{self.submission.pk}/grade/",
            {"action": "revision", "revision_notes": "  "},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "/api/submissions/99999/grade/",
            {"action": "grade", "numeric_score": 80},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_student_and_non_owner_teacher_are_forbidden(self):
        for user in (self.student, self.other_teacher):
            self.client.force_authenticate(user)
            response = self.client.post(
                f"/api/submissions/{self.submission.pk}/grade/",
                {"action": "grade", "numeric_score": 80},
                format="json",
            )
            self.assertEqual(response.status_code, 403)


    @patch("api.views.firebase_utils.send_notification_to_user")
    def test_regrade_updates_submission_in_place(self, notify):
        self.client.force_authenticate(self.teacher)
        first = self.client.post(
            f"/api/submissions/{self.submission.pk}/grade/",
            {"action": "grade", "numeric_score": 80, "teacher_feedback": "Good start."},
            format="json",
        )
        self.assertEqual(first.status_code, 200)

        second = self.client.post(
            f"/api/submissions/{self.submission.pk}/grade/",
            {"action": "grade", "numeric_score": 95, "teacher_feedback": "Excellent work."},
            format="json",
        )

        self.assertEqual(second.status_code, 200)
        self.submission.refresh_from_db()
        self.assertEqual(AssignmentSubmission.objects.filter(pk=self.submission.pk).count(), 1)
        self.assertEqual(self.submission.numeric_score, 95)
        self.assertEqual(self.submission.grade, "A")
        self.assertEqual(self.submission.teacher_feedback, "Excellent work.")
        self.assertEqual(notify.call_count, 2)


class ChatApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username="chat_teacher",
            email="chat-teacher@example.com",
            password="test-password",
            user_type="teacher",
        )
        self.student = User.objects.create_user(
            username="chat_student",
            email="chat-student@example.com",
            password="test-password",
            user_type="student",
        )
        self.other_student = User.objects.create_user(
            username="chat_other",
            email="chat-other@example.com",
            password="test-password",
            user_type="student",
        )

    def test_student_opens_and_reuses_teacher_chat(self):
        self.client.force_authenticate(self.student)
        created = self.client.post("/api/chat/rooms/with-teacher/", {}, format="json")
        reused = self.client.post("/api/chat/rooms/with-teacher/", {}, format="json")

        self.assertEqual(created.status_code, 201)
        self.assertEqual(reused.status_code, 200)
        self.assertEqual(created.json()["id"], reused.json()["id"])
        self.assertEqual(ChatRoom.objects.count(), 1)
        self.assertEqual(ChatRoom.objects.get().participants.count(), 2)

    def test_teacher_chat_requires_student_role(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.post("/api/chat/rooms/with-teacher/", {}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_teacher_chat_returns_404_without_active_teacher(self):
        self.teacher.is_active = False
        self.teacher.save(update_fields=["is_active"])
        self.client.force_authenticate(self.student)
        response = self.client.post("/api/chat/rooms/with-teacher/", {}, format="json")
        self.assertEqual(response.status_code, 404)

    def test_chat_messages_are_scoped_to_participants(self):
        room = ChatRoom.objects.create(
            name="Private chat",
            created_by=self.student,
            is_group_chat=False,
        )
        room.participants.add(self.student, self.teacher)
        Message.objects.create(room=room, sender=self.teacher, content="Welcome")

        self.client.force_authenticate(self.other_student)
        response = self.client.get(f"/api/chat/rooms/{room.pk}/messages/")
        self.assertEqual(response.status_code, 404)

    def test_room_list_returns_newest_latest_message(self):
        room = ChatRoom.objects.create(
            name="Latest message",
            created_by=self.student,
            is_group_chat=False,
        )
        room.participants.add(self.student, self.teacher)
        Message.objects.create(room=room, sender=self.student, content="Older")
        Message.objects.create(room=room, sender=self.teacher, content="Newest")

        self.client.force_authenticate(self.student)
        response = self.client.get("/api/chat/rooms/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["results"][0]["latest_message"]["content"],
            "Newest",
        )
