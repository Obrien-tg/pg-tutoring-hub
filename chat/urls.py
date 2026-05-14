from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("", views.chat_rooms_list, name="rooms_list"),
    path("room/<int:room_id>/", views.chat_room, name="room"),
    path("create/", views.create_chat_room, name="create_room"),
]
