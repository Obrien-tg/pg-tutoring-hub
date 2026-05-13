import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from users.models import FirebaseToken

logger = logging.getLogger(__name__)


@method_decorator(login_required, name="dispatch")
class FirebaseTokenView(View):
    """Handle Firebase Cloud Messaging token registration"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            token = data.get("token")
            device_info = data.get(
                "device_info", request.META.get("HTTP_USER_AGENT", "")
            )

            if not token:
                return JsonResponse({"error": "Token is required"}, status=400)

            # Create or update token
            firebase_token, created = FirebaseToken.objects.get_or_create(
                user=request.user,
                token=token,
                defaults={"device_info": device_info, "is_active": True},
            )

            if not created:
                # Update existing token
                firebase_token.device_info = device_info
                firebase_token.is_active = True
                firebase_token.save()

            logger.info(
                f"Firebase token {'created' if created else 'updated'} for user {request.user.username}"
            )

            return JsonResponse(
                {"success": True, "message": "Token registered successfully"}
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Error registering Firebase token: {str(e)}")
            return JsonResponse({"error": "Internal server error"}, status=500)

    def delete(self, request):
        """Deactivate Firebase token"""
        try:
            data = json.loads(request.body)
            token = data.get("token")

            if not token:
                return JsonResponse({"error": "Token is required"}, status=400)

            # Deactivate token
            tokens_updated = FirebaseToken.objects.filter(
                user=request.user, token=token
            ).update(is_active=False)

            if tokens_updated > 0:
                logger.info(
                    f"Firebase token deactivated for user {request.user.username}"
                )
                return JsonResponse(
                    {"success": True, "message": "Token deactivated successfully"}
                )
            else:
                return JsonResponse({"error": "Token not found"}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Error deactivating Firebase token: {str(e)}")
            return JsonResponse({"error": "Internal server error"}, status=500)


@require_http_methods(["POST"])
@login_required
def send_test_notification(request):
    """Send a test notification to the user's devices"""
    try:
        from .firebase_utils import send_notification_to_user

        # Get user's active tokens
        tokens = FirebaseToken.objects.filter(user=request.user, is_active=True)

        if not tokens.exists():
            return JsonResponse(
                {"error": "No active Firebase tokens found for this user"}, status=400
            )

        # Send test notification
        notification_data = {
            "title": "Test Notification",
            "body": "This is a test notification from PG Tutoring Hub!",
            "icon": "/static/img/logo.png",
        }

        success_count = send_notification_to_user(request.user, notification_data)

        return JsonResponse(
            {
                "success": True,
                "message": f"Test notification sent to {success_count} device(s)",
            }
        )

    except ImportError:
        return JsonResponse(
            {"error": "Firebase notifications not configured"}, status=503
        )
    except Exception as e:
        logger.error(f"Error sending test notification: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)


@require_http_methods(["GET"])
@login_required
def firebase_config(request):
    """Return Firebase configuration for frontend"""
    config = {
        "apiKey": getattr(settings, "FIREBASE_API_KEY", ""),
        "authDomain": getattr(settings, "FIREBASE_AUTH_DOMAIN", ""),
        "projectId": getattr(settings, "FIREBASE_PROJECT_ID", ""),
        "storageBucket": getattr(settings, "FIREBASE_STORAGE_BUCKET", ""),
        "messagingSenderId": getattr(settings, "FIREBASE_MESSAGING_SENDER_ID", ""),
        "appId": getattr(settings, "FIREBASE_APP_ID", ""),
        "vapidKey": getattr(settings, "FIREBASE_VAPID_KEY", ""),
    }

    # Only return config if at least basic settings are present
    if config.get("projectId"):
        return JsonResponse({"config": config})
    else:
        return JsonResponse(
            {"error": "Firebase not configured", "config": None}, status=503
        )
