from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .models import ChatRoom, Message


@login_required
def chat_rooms_list(request):
    """List all chat rooms for the user"""
    rooms = ChatRoom.objects.filter(participants=request.user)
    return render(request, "chat/rooms_list.html", {"rooms": rooms})


@login_required
def chat_room(request, room_id):
    """Show a specific chat room"""
    room = get_object_or_404(ChatRoom, pk=room_id)
    if not room.participants.filter(pk=request.user.pk).exists():
        return HttpResponseForbidden("You do not have access to this chat room.")

    if request.method == "POST":
        content = request.POST.get("message", "").strip()
        if not content:
            django_messages.error(request, "Message cannot be empty.")
        else:
            Message.objects.create(room=room, sender=request.user, content=content)
            return redirect("chat:room", room_id=room.pk)

    chat_messages = room.messages.all().order_by("timestamp")
    return render(
        request, "chat/room.html", {"room": room, "chat_messages": chat_messages}
    )


@login_required
def create_chat_room(request):
    """Create a new chat room"""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        participants_raw = request.POST.get("participants", "")
        participants = [p.strip() for p in participants_raw.split(",") if p.strip()]
        user_model = get_user_model()
        selected_users = []
        unknown_users = []

        for participant in participants:
            try:
                lookup = {"pk": int(participant)} if participant.isdigit() else {
                    "username": participant
                }
                selected_users.append(user_model.objects.get(**lookup))
            except (TypeError, ValueError, user_model.DoesNotExist):
                unknown_users.append(participant)

        if not name:
            django_messages.error(request, "A room name is required.")
            return render(request, "chat/create_room.html")
        if unknown_users:
            django_messages.error(
                request,
                "Unknown participant(s): " + ", ".join(unknown_users),
            )
            return render(request, "chat/create_room.html")

        room = ChatRoom.objects.create(name=name, created_by=request.user)
        room.participants.add(request.user, *selected_users)
        return redirect("chat:room", room_id=room.pk)
    return render(request, "chat/create_room.html")
