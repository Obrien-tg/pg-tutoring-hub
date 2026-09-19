from django.urls import path

from .views import (
    AssignmentSubmissionView,
    AssignmentsView,
    DashboardView,
    LoginView,
    LogoutView,
    MaterialsView,
    MeView,
    ProgressView,
    RoomMessagesView,
    RoomsView,
)

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("materials/", MaterialsView.as_view(), name="materials"),
    path("assignments/", AssignmentsView.as_view(), name="assignments"),
    path(
        "assignments/<int:assignment_id>/submissions/",
        AssignmentSubmissionView.as_view(),
        name="assignment-submission",
    ),
    path("chat/rooms/", RoomsView.as_view(), name="rooms"),
    path("chat/rooms/<int:room_id>/messages/", RoomMessagesView.as_view(), name="room-messages"),
    path("progress/", ProgressView.as_view(), name="progress"),
]
