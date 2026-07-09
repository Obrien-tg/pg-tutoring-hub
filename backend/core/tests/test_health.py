from django.test import TestCase


class HealthCheckTest(TestCase):
    def test_healthz(self):
        resp = self.client.get("/healthz", secure=True)
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(resp.content, {"status": "ok"})
