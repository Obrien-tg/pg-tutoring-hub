from django.test import TestCase
from django.urls import reverse


class HealthCheckTest(TestCase):
    def test_healthz(self):
        resp = self.client.get('/healthz')
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(resp.content, {"status": "ok"})
