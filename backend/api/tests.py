from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from hub.models import Assignment, AssignmentSubmission, Material, Subject

User = get_user_model()


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
