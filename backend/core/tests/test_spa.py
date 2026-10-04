from django.contrib.auth import get_user_model
from django.test import TestCase


class SpaRoutingTests(TestCase):
    def test_root_serves_spa_shell_with_csrf_token(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="root"')
        self.assertRegex(response.content.decode(), r'<meta name="csrf-token" content="[^"]+">')

    def test_authenticated_student_dashboard_stays_json(self):
        user = get_user_model().objects.create_user(
            username="spa_student",
            password="test-password",
            email="spa@example.com",
            user_type="student",
            grade_level="5",
            parent_email="parent@example.com",
        )
        self.client.force_login(user)

        response = self.client.get("/api/dashboard/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json()["role"], "student")

    def test_unauthenticated_api_auth_stays_json(self):
        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("detail", response.json())
