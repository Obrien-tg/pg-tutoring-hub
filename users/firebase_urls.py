from django.urls import path

from .firebase_views import (FirebaseTokenView, firebase_config,
                             send_test_notification)

urlpatterns = [
    path("token/", FirebaseTokenView.as_view(), name="firebase_token"),
    path("test-notification/", send_test_notification, name="test_notification"),
    path("config/", firebase_config, name="firebase_config"),
]
