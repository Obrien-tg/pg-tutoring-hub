from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from hub.models import Assignment, AssignmentSubmission, Material, Subject

User = get_user_model()


class StudentDashboardNextAssignmentTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="dashboard_teacher",
            email="dashboard-teacher@example.com",
            password="testpass123",
            user_type="teacher",
        )
        self.student = User.objects.create_user(
            username="dashboard_student",
            email="dashboard-student@example.com",
            password="testpass123",
            user_type="student",
            grade_level="5",
            parent_email="parent@example.com",
        )
        self.subject = Subject.objects.create(name="Dashboard Math")
        self.material = Material.objects.create(
            title="Fractions Worksheet",
            description="Practice fractions",
            material_type="worksheet",
            subject=self.subject,
            difficulty_level="beginner",
            grade_level="5",
            estimated_time=30,
            uploaded_by=self.teacher,
            external_link="https://example.com/fractions",
        )

    def _make_assignment(self, title, days_from_now):
        assignment = Assignment.objects.create(
            title=title,
            description=f"Do {title}",
            material=self.material,
            due_date=timezone.now() + timedelta(days=days_from_now),
            created_by=self.teacher,
            is_active=True,
        )
        assignment.assigned_to.add(self.student)
        return assignment

    def _dashboard(self):
        self.client.force_login(self.student)
        return self.client.get(reverse("dashboard:student"))

    def test_next_assignment_is_earliest_unsubmitted(self):
        earlier = self._make_assignment("Early HW", 2)
        self._make_assignment("Later HW", 5)

        response = self._dashboard()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["next_assignment"], earlier)

    def test_submitted_assignment_is_skipped(self):
        earlier = self._make_assignment("Already Done", 1)
        later = self._make_assignment("Still Todo", 4)
        AssignmentSubmission.objects.create(
            assignment=earlier,
            student=self.student,
            submission_text="I finished it",
            status="submitted",
        )

        response = self._dashboard()

        self.assertEqual(response.context["next_assignment"], later)

    def test_revision_requested_becomes_next(self):
        assignment = self._make_assignment("Needs Fixes", 3)
        submission = AssignmentSubmission.objects.create(
            assignment=assignment,
            student=self.student,
            submission_text="First attempt",
            status="returned",
            revision_requested=True,
            revision_notes="Please show your working.",
        )

        response = self._dashboard()

        self.assertEqual(response.context["next_assignment"], assignment)
        self.assertEqual(
            response.context["next_assignment_submission"],
            submission,
        )

    def test_all_caught_up_when_nothing_left(self):
        assignment = self._make_assignment("Only One", 2)
        AssignmentSubmission.objects.create(
            assignment=assignment,
            student=self.student,
            submission_text="Done",
            status="submitted",
        )

        response = self._dashboard()

        self.assertIsNone(response.context["next_assignment"])
