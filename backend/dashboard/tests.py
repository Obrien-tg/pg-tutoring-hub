from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from hub.models import Assignment, AssignmentSubmission, Material, StudentProgress, Subject
from users.models import CustomUser


class StudentDashboardTests(TestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            username="dashboard_student",
            password="pass1234",
            user_type="student",
            grade_level="5",
            parent_email="parent@example.com",
        )
        self.teacher = CustomUser.objects.create_user(
            username="dashboard_teacher",
            password="pass1234",
            user_type="teacher",
        )
        self.subject = Subject.objects.create(name="Mathematics", color_code="#1B7A5F")
        self.material = Material.objects.create(
            title="Fractions",
            description="Learn fractions",
            material_type="worksheet",
            subject=self.subject,
            difficulty_level="beginner",
            external_link="https://example.com/fractions",
            grade_level="5",
            estimated_time=30,
            uploaded_by=self.teacher,
        )
        self.assignment = Assignment.objects.create(
            title="Fraction practice",
            description="Practice equivalent fractions",
            material=self.material,
            due_date=timezone.now() + timedelta(days=2),
            created_by=self.teacher,
        )
        self.assignment.assigned_to.add(self.student)

    def test_student_dashboard_prioritizes_next_assignment(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("dashboard:student"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["next_assignment"], self.assignment)
        self.assertContains(response, "DO NOW")
        self.assertContains(response, "Fraction practice")

    def test_student_dashboard_uses_real_graded_feedback(self):
        AssignmentSubmission.objects.create(
            assignment=self.assignment,
            student=self.student,
            submission_text="My answer",
            status="graded",
            grade="A",
            numeric_score=94,
            teacher_feedback="Great explanation!",
        )
        self.client.force_login(self.student)

        response = self.client.get(reverse("dashboard:student"))

        self.assertContains(response, "Great explanation!")
        self.assertContains(response, "A")

    def test_student_dashboard_exposes_subject_mastery_from_progress(self):
        started_at = timezone.now() - timedelta(hours=1)
        StudentProgress.objects.create(
            student=self.student,
            material=self.material,
            status="completed",
            started_at=started_at,
            completed_at=timezone.now(),
            time_spent_minutes=25,
        )
        self.client.force_login(self.student)

        response = self.client.get(reverse("dashboard:student"))

        self.assertEqual(response.context["subject_mastery"][0]["percentage"], 100)
        self.assertContains(response, "Mathematics")
        self.assertContains(response, "100%")
