from django.test import TestCase


class CsrfEndpointTests(TestCase):
    def test_csrf_endpoint_sets_cookie_and_returns_token(self):
        response = self.client.get("/api/csrf/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", response.cookies)
        self.assertTrue(response.json()["csrfToken"])
