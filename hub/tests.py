import tempfile
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from hub.models import Assignment, AssignmentSubmission, Material, Subject
from users.models import FirebaseToken

User = get_user_model()


class AssignmentSubmissionTestCase(TestCase):
    """Test cases for assignment submission functionality"""

    def setUp(self):
        """Set up test data"""
        # Create users
        self.teacher = User.objects.create_user(
            username="teacher1",
            email="teacher@example.com",
            password="password123",
            user_type="teacher",
            first_name="John",
            last_name="Doe",
        )

        self.student = User.objects.create_user(
            username="student1",
            email="student@example.com",
            password="password123",
            user_type="student",
            first_name="Jane",
            last_name="Smith",
            grade_level="9",
            parent_email="parent@example.com",
        )

        # Create Firebase token for teacher
        FirebaseToken.objects.create(
            user=self.teacher, token="test_fcm_token_teacher", is_active=True
        )

        # Create subject and material
        self.subject = Subject.objects.create(
            name="Mathematics", description="Math subject"
        )

        self.material = Material.objects.create(
            title="Algebra Worksheet",
            description="Basic algebra problems",
            material_type="worksheet",
            subject=self.subject,
            difficulty_level="intermediate",
            grade_level="9",
            estimated_time=60,
            uploaded_by=self.teacher,
            external_link="https://example.com/algebra.pdf",
        )

        # Create assignment
        self.assignment = Assignment.objects.create(
            title="Complete Algebra Worksheet",
            description="Solve all problems",
            material=self.material,
            due_date=timezone.now() + timezone.timedelta(days=7),
            created_by=self.teacher,
        )
        self.assignment.assigned_to.add(self.student)

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_successful_assignment_submission_with_file(self):
        """Test successful assignment submission with file upload"""
        self.client.force_login(self.student)

        # Create a test file
        test_file = ContentFile(b"Test file content", name="test_submission.pdf")

        response = self.client.post(
            reverse("hub:submit_assignment", args=[self.assignment.id]),
            {
                "submission_text": "Here is my solution",
                "submission_notes": "Please review carefully",
                "submission_file": test_file,
            },
        )

        # Check redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("hub:assignments_list"))

        # Check submission was created
        submission = AssignmentSubmission.objects.get(
            assignment=self.assignment, student=self.student
        )
        self.assertEqual(submission.submission_text, "Here is my solution")
        self.assertEqual(submission.submission_notes, "Please review carefully")
        self.assertIsNotNone(submission.submission_file)
        self.assertEqual(submission.status, "submitted")

    def test_successful_assignment_submission_text_only(self):
        """Test successful assignment submission with text only"""
        self.client.force_login(self.student)

        response = self.client.post(
            reverse("hub:submit_assignment", args=[self.assignment.id]),
            {
                "submission_text": "Here is my text solution",
                "submission_notes": "No file needed",
            },
        )

        self.assertEqual(response.status_code, 302)

        submission = AssignmentSubmission.objects.get(
            assignment=self.assignment, student=self.student
        )
        self.assertEqual(submission.submission_text, "Here is my text solution")
        self.assertIsNone(submission.submission_file)

    def test_submission_validation_requires_content(self):
        """Test that submission requires either text or file"""
        self.client.login(username="student1", password="password123")

        response = self.client.post(
            reverse("hub:submit_assignment", args=[self.assignment.id]),
            {"submission_notes": "Empty submission"},
        )

        # Should return to form with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Please provide either text submission or upload a file"
        )

        # No submission should be created
        self.assertFalse(
            AssignmentSubmission.objects.filter(
                assignment=self.assignment, student=self.student
            ).exists()
        )

    def test_unauthorized_user_cannot_submit(self):
        """Test that unauthorized users cannot submit assignments"""
        # Create another student not assigned to this assignment
        other_student = User.objects.create_user(
            username="student2",
            email="student2@example.com",
            password="password123",
            user_type="student",
            grade_level="10",
            parent_email="parent2@example.com",
        )
        self.client.login(username="student2", password="password123")

        response = self.client.post(
            reverse("hub:submit_assignment", args=[self.assignment.id]),
            {"submission_text": "Unauthorized submission"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("hub:assignments_list"))

        # Check error message
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("not authorized", str(messages[0]))

    def test_teacher_cannot_submit_assignment(self):
        """Test that teachers cannot submit assignments"""
        self.client.login(username="teacher1", password="password123")

        response = self.client.post(
            reverse("hub:submit_assignment", args=[self.assignment.id]),
            {"submission_text": "Teacher trying to submit"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("hub:assignments_list"))

    def test_resubmission_updates_existing(self):
        """Test that resubmitting updates existing submission"""
        # Create initial submission
        AssignmentSubmission.objects.create(
            assignment=self.assignment,
            student=self.student,
            submission_text="Initial submission",
            status="submitted",
        )

        self.client.force_login(self.student)

        response = self.client.post(
            reverse("hub:submit_assignment", args=[self.assignment.id]),
            {"submission_text": "Updated submission"},
        )

        self.assertEqual(response.status_code, 302)

        # Should still be only one submission
        submissions = AssignmentSubmission.objects.filter(
            assignment=self.assignment, student=self.student
        )
        self.assertEqual(submissions.count(), 1)

        submission = submissions.first()
        self.assertEqual(submission.submission_text, "Updated submission")

    def test_get_submission_form(self):
        """Test getting the submission form"""
        self.client.force_login(self.student)

        response = self.client.get(
            reverse("hub:submit_assignment", args=[self.assignment.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hub/submit_assignment.html")
        self.assertEqual(response.context["assignment"], self.assignment)
        self.assertIsNone(response.context["existing_submission"])

    @patch("users.firebase_utils.send_submission_notification")
    def test_submission_triggers_firebase_push(self, mock_send_notification):
        """Test that assignment submission triggers Firebase push notification"""
        self.client.force_login(self.student)

        response = self.client.post(
            reverse("hub:submit_assignment", args=[self.assignment.id]),
            {"submission_text": "Test submission for Firebase"},
        )

        self.assertEqual(response.status_code, 302)

        # Check that Firebase notification was called
        mock_send_notification.assert_called_once()
        submission = AssignmentSubmission.objects.get(
            assignment=self.assignment, student=self.student
        )
        mock_send_notification.assert_called_with(submission)
