from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


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
