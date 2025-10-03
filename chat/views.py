from django.shortcuts import render, get_object_or_404, redirect
from .models import ChatRoom, Message
from django.contrib.auth.decorators import login_required

@login_required
def chat_rooms_list(request):
    """List all chat rooms for the user"""
    rooms = ChatRoom.objects.filter(participants=request.user)
    return render(request, 'chat/rooms_list.html', {'rooms': rooms})

@login_required
def chat_room(request, room_id):
    """Show a specific chat room"""
    room = get_object_or_404(ChatRoom, pk=room_id)
    messages = room.messages.all().order_by('timestamp')
    return render(request, 'chat/room.html', {'room': room, 'messages': messages})

@login_required
def create_chat_room(request):
    """Create a new chat room"""
    if request.method == 'POST':
        name = request.POST.get('name')
        participants_raw = request.POST.get('participants', '')
        participants = [p.strip() for p in participants_raw.split(',') if p.strip()]
        room = ChatRoom.objects.create(name=name, created_by=request.user)
        # Attempt to add participants by id or username
        for pid in participants:
            try:
                if pid.isdigit():
                    user = request.user._meta.model.objects.get(pk=int(pid))
                else:
                    user = request.user._meta.model.objects.get(username=pid)
                room.participants.add(user)
            except Exception:
                continue
        room.participants.add(request.user)
        return redirect('chat:room', room_id=room.pk)
    return render(request, 'chat/create_room.html')
