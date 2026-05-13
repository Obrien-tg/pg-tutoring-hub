from django.conf import settings
from django.test import SimpleTestCase


class SettingsTest(SimpleTestCase):
    def test_admin_url_present(self):
        self.assertTrue(hasattr(settings, "ADMIN_URL"))
        self.assertTrue(settings.ADMIN_URL.endswith("/"))
