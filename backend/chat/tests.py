from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ChatRoom, Message


class ChatViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.teacher = user_model.objects.create_user(
            username="teacher", password="pass1234", user_type="teacher"
        )
        self.student = user_model.objects.create_user(
            username="student",
            password="pass1234",
            user_type="student",
            grade_level="8",
            parent_email="parent@example.com",
        )
        self.other_student = user_model.objects.create_user(
            username="other",
            password="pass1234",
            user_type="student",
            grade_level="8",
            parent_email="parent@example.com",
        )
        self.room = ChatRoom.objects.create(name="Tutoring", created_by=self.teacher)
        self.room.participants.add(self.teacher, self.student)

    def login(self, user):
        self.client.force_login(user)

    def test_rooms_list_requires_login(self):
        response = self.client.get(reverse("chat:rooms_list"))
        self.assertEqual(response.status_code, 302)

    def test_room_requires_login(self):
        response = self.client.get(reverse("chat:room", args=[self.room.pk]))
        self.assertEqual(response.status_code, 302)

    def test_participant_can_view_room(self):
        self.login(self.student)
        response = self.client.get(reverse("chat:room", args=[self.room.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No messages yet")

    def test_non_participant_cannot_view_room(self):
        self.login(self.other_student)
        response = self.client.get(reverse("chat:room", args=[self.room.pk]))
        self.assertEqual(response.status_code, 403)

    def test_participant_can_post_message(self):
        self.login(self.student)
        response = self.client.post(
            reverse("chat:room", args=[self.room.pk]), {"message": "Hello teacher"}
        )
        self.assertRedirects(response, reverse("chat:room", args=[self.room.pk]))
        self.assertTrue(
            Message.objects.filter(
                room=self.room, sender=self.student, content="Hello teacher"
            ).exists()
        )

    def test_non_participant_cannot_post_message(self):
        self.login(self.other_student)
        response = self.client.post(
            reverse("chat:room", args=[self.room.pk]), {"message": "Secret"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Message.objects.filter(content="Secret").exists())

    def test_empty_message_is_not_saved(self):
        self.login(self.student)
        response = self.client.post(
            reverse("chat:room", args=[self.room.pk]), {"message": "  "}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.filter(room=self.room).count(), 0)
        self.assertContains(response, "Message cannot be empty")

    def test_room_renders_messages(self):
        Message.objects.create(room=self.room, sender=self.teacher, content="Welcome")
        self.login(self.student)
        response = self.client.get(reverse("chat:room", args=[self.room.pk]))
        self.assertContains(response, "Welcome")

    def test_create_room_accepts_usernames(self):
        self.login(self.teacher)
        response = self.client.post(
            reverse("chat:create_room"),
            {"name": "New room", "participants": self.student.username},
        )
        room = ChatRoom.objects.get(name="New room")
        self.assertRedirects(response, reverse("chat:room", args=[room.pk]))
        self.assertQuerySetEqual(
            room.participants.order_by("pk"),
            [self.teacher, self.student],
            transform=lambda user: user,
        )

    def test_create_room_accepts_user_ids(self):
        self.login(self.teacher)
        response = self.client.post(
            reverse("chat:create_room"),
            {"name": "ID room", "participants": str(self.student.pk)},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ChatRoom.objects.filter(name="ID room").exists())

    def test_create_room_reports_unknown_users(self):
        self.login(self.teacher)
        response = self.client.post(
            reverse("chat:create_room"),
            {"name": "Invalid room", "participants": "missing-user"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unknown participant(s): missing-user")
        self.assertFalse(ChatRoom.objects.filter(name="Invalid room").exists())
