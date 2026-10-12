from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from rest_framework.test import APIClient

from .models import ParentChildLink


User = get_user_model()


class ParentChildLinkTests(TestCase):
    def setUp(self):
        self.parent = User.objects.create_user(
            username="parent",
            email="parent@example.com",
            password="test-password",
            user_type="parent",
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="test-password",
            user_type="student",
            grade_level="5",
            parent_email="parent@example.com",
        )

    def test_link_defaults_to_active(self):
        link = ParentChildLink.objects.create(
            parent=self.parent,
            student=self.student,
        )

        self.assertTrue(link.is_active)

    def test_duplicate_parent_student_pair_is_rejected(self):
        ParentChildLink.objects.create(parent=self.parent, student=self.student)

        with self.assertRaises((IntegrityError, ValidationError)):
            ParentChildLink.objects.create(
                parent=self.parent,
                student=self.student,
            )


class ParentChildApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.parent = User.objects.create_user(
            username="api_parent",
            email="api-parent@example.com",
            password="test-password",
            user_type="parent",
        )
        self.other_parent = User.objects.create_user(
            username="other_parent",
            email="other-parent@example.com",
            password="test-password",
            user_type="parent",
        )
        self.student = User.objects.create_user(
            username="api_student",
            email="api-student@example.com",
            password="test-password",
            user_type="student",
            grade_level="5",
            parent_email="api-parent@example.com",
            first_name="Api",
            last_name="Student",
        )
        self.other_student = User.objects.create_user(
            username="other_student",
            email="other-student@example.com",
            password="test-password",
            user_type="student",
            grade_level="6",
            parent_email="other-parent@example.com",
        )
        ParentChildLink.objects.create(parent=self.parent, student=self.student)
        ParentChildLink.objects.create(
            parent=self.other_parent,
            student=self.other_student,
        )

    def test_parent_sees_only_active_children(self):
        self.client.force_authenticate(self.parent)

        response = self.client.get("/api/parent/children/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["student"], self.student.id)
        self.assertEqual(response.json()[0]["student_name"], "Api Student")
        self.assertEqual(response.json()[0]["student_email"], "api-student@example.com")
        self.assertTrue(response.json()[0]["is_active"])

    def test_student_is_forbidden(self):
        self.client.force_authenticate(self.student)

        self.assertEqual(self.client.get("/api/parent/children/").status_code, 403)

    def test_unauthenticated_user_is_unauthorized(self):
        response = self.client.get("/api/parent/children/")

        self.assertEqual(response.status_code, 401)
