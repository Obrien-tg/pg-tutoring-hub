import json
import logging
from typing import Any, Dict, List

import firebase_admin
from django.conf import settings
from firebase_admin import credentials, messaging

from users.models import CustomUser, FirebaseToken

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
_firebase_app = None


def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_app

    if _firebase_app is not None:
        return _firebase_app

    try:
        # Check if we have the service account key
        service_account_path = getattr(settings, "FIREBASE_SERVICE_ACCOUNT_KEY", None)

        if service_account_path:
            # Initialize with service account key file
            cred = credentials.Certificate(service_account_path)
            _firebase_app = firebase_admin.initialize_app(cred)
        else:
            # Try to initialize with environment variables (for production)
            project_id = getattr(settings, "FIREBASE_PROJECT_ID", None)
            if project_id:
                # This will use Application Default Credentials
                _firebase_app = firebase_admin.initialize_app(
                    options={"projectId": project_id}
                )
            else:
                logger.warning(
                    "Firebase not properly configured - notifications disabled"
                )
                return None

        logger.info("Firebase Admin SDK initialized successfully")
        return _firebase_app

    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
        return None


def send_notification_to_tokens(
    tokens: List[str], notification_data: Dict[str, Any], data: Dict[str, str] = None
) -> int:
    """
    Send notification to specific FCM tokens

    Args:
        tokens: List of FCM tokens
        notification_data: Notification payload with title, body, etc.
        data: Optional data payload

    Returns:
        Number of successful sends
    """
    if not tokens:
        return 0

    app = initialize_firebase()
    if not app:
        logger.error("Firebase not initialized - cannot send notifications")
        return 0

    try:
        # Create notification
        notification = messaging.Notification(
            title=notification_data.get("title", "PG Tutoring Hub"),
            body=notification_data.get("body", "You have a new message"),
            image=notification_data.get("image"),
        )

        # Create Android-specific config
        android_config = messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
                icon=notification_data.get("icon", "/static/img/logo.png"),
                color="#FFC107",  # Sunshine yellow from our theme
                sound="default",
                priority="high",
            )
        )

        # Create web push config
        web_config = messaging.WebpushConfig(
            notification=messaging.WebpushNotification(
                icon=notification_data.get("icon", "/static/img/logo.png"),
                badge="/static/img/badge.png",
                tag="pg-tutoring-notification",
                require_interaction=True,
            )
        )

        # Create message
        message = messaging.MulticastMessage(
            notification=notification,
            data=data or {},
            tokens=tokens,
            android=android_config,
            webpush=web_config,
        )

        # Send the message
        response = messaging.send_multicast(message)

        # Log results
        logger.info(
            f"Notification sent: {response.success_count} successful, {response.failure_count} failed"
        )

        # Handle failed tokens
        if response.failure_count > 0:
            failed_tokens = []
            for idx, result in enumerate(response.responses):
                if not result.success:
                    failed_tokens.append(tokens[idx])
                    logger.warning(
                        f"Failed to send to token {tokens[idx]}: {result.exception}"
                    )

            # Deactivate invalid tokens
            FirebaseToken.objects.filter(token__in=failed_tokens).update(
                is_active=False
            )

        return response.success_count

    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return 0


def send_notification_to_user(
    user: CustomUser, notification_data: Dict[str, Any], data: Dict[str, str] = None
) -> int:
    """
    Send notification to all active devices of a user

    Args:
        user: User to send notification to
        notification_data: Notification payload
        data: Optional data payload

    Returns:
        Number of successful sends
    """
    # Get active tokens for the user
    active_tokens = FirebaseToken.objects.filter(user=user, is_active=True).values_list(
        "token", flat=True
    )

    if not active_tokens:
        logger.info(f"No active FCM tokens found for user {user.username}")
        return 0

    return send_notification_to_tokens(list(active_tokens), notification_data, data)


def send_notification_to_users(
    users: List[CustomUser],
    notification_data: Dict[str, Any],
    data: Dict[str, str] = None,
) -> int:
    """
    Send notification to multiple users

    Args:
        users: List of users to send notification to
        notification_data: Notification payload
        data: Optional data payload

    Returns:
        Total number of successful sends
    """
    user_ids = [user.id for user in users]

    # Get all active tokens for these users
    active_tokens = FirebaseToken.objects.filter(
        user__id__in=user_ids, is_active=True
    ).values_list("token", flat=True)

    if not active_tokens:
        logger.info(f"No active FCM tokens found for {len(users)} users")
        return 0

    return send_notification_to_tokens(list(active_tokens), notification_data, data)


def send_assignment_notification(assignment, action="created"):
    """Send notification about assignment updates"""
    if action == "created":
        title = "New Assignment"
        body = f"You have a new assignment: {assignment.title}"
    elif action == "graded":
        title = "Assignment Graded"
        body = f"Your assignment '{assignment.title}' has been graded"
    elif action == "due_soon":
        title = "Assignment Due Soon"
        body = f"Assignment '{assignment.title}' is due soon"
    else:
        return 0

    notification_data = {
        "title": title,
        "body": body,
        "icon": "/static/img/assignment-icon.png",
    }

    data = {"type": "assignment", "assignment_id": str(assignment.id), "action": action}

    # Send to the student
    return send_notification_to_user(assignment.student, notification_data, data)


def send_chat_notification(message, room):
    """Send notification about new chat messages"""
    notification_data = {
        "title": f"New message in {room.name}",
        "body": f"{message.user.first_name or message.user.username}: {message.content[:50]}...",
        "icon": "/static/img/chat-icon.png",
    }

    data = {"type": "chat", "room_id": str(room.id), "message_id": str(message.id)}

    # Send to all room participants except the sender
    participants = room.participants.exclude(id=message.user.id)
    return send_notification_to_users(list(participants), notification_data, data)


def send_progress_notification(user, achievement):
    """Send notification about progress milestones"""
    notification_data = {
        "title": "Achievement Unlocked! 🎉",
        "body": f"Congratulations! You've {achievement}",
        "icon": "/static/img/achievement-icon.png",
    }

    data = {"type": "achievement", "achievement": achievement}

    return send_notification_to_user(user, notification_data, data)


# Utility function to clean up inactive tokens
def cleanup_inactive_tokens():
    """Remove tokens that are no longer valid"""
    from datetime import timedelta

    from django.utils import timezone

    # Remove tokens that haven't been used in 30 days
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count = FirebaseToken.objects.filter(updated_at__lt=cutoff_date).delete()[0]

    logger.info(f"Cleaned up {deleted_count} inactive Firebase tokens")
    return deleted_count
