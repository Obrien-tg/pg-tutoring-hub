from django.urls import path

from .views import (
    AssignmentSubmissionView,
    GradeSubmissionView,
    AssignmentsView,
    AssignmentDetailView,
    csrf_view,
    DashboardView,
    LoginView,
    LogoutView,
    MaterialDetailView,
    MaterialsView,
    MeView,
    ParentChildrenListView,
    ParentChildProgressView,
    PasswordResetView,
    ProgressView,
    RoomMessagesView,
    RoomsView,
    TeacherChatView,
)

urlpatterns = [
    path("csrf/", csrf_view, name="csrf"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/password/reset/", PasswordResetView.as_view(), name="password-reset"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("materials/", MaterialsView.as_view(), name="materials"),
    path(
        "materials/<int:material_id>/",
        MaterialDetailView.as_view(),
        name="material-detail",
    ),
    path("assignments/", AssignmentsView.as_view(), name="assignments"),
    path("assignments/<int:assignment_id>/", AssignmentDetailView.as_view(), name="assignment-detail"),
    path(
        "assignments/<int:assignment_id>/submissions/",
        AssignmentSubmissionView.as_view(),
        name="assignment-submission",
    ),
    path(
        "submissions/<int:submission_id>/grade/",
        GradeSubmissionView.as_view(),
        name="grade-submission",
    ),
    path("chat/rooms/", RoomsView.as_view(), name="rooms"),
    path("chat/rooms/with-teacher/", TeacherChatView.as_view(), name="teacher-chat"),
    path("chat/rooms/<int:room_id>/messages/", RoomMessagesView.as_view(), name="room-messages"),
    path("progress/", ProgressView.as_view(), name="progress"),
    path("parent/children/", ParentChildrenListView.as_view(), name="parent-children"),
    path(
        "parent/children/<int:student_id>/progress/",
        ParentChildProgressView.as_view(),
        name="parent-child-progress",
    ),
]
