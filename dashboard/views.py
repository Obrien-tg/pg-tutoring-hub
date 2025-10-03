from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from hub.models import Material, Assignment, StudentProgress
from chat.models import ChatRoom, Message
from django.contrib import messages
from .forms import CreateMaterialForm, CreateAssignmentForm, AnnouncementForm

User = get_user_model()

@login_required
def dashboard_index(request):
    """Redirect users to their appropriate dashboard based on user type"""
    if request.user.is_teacher:
        return redirect('dashboard:teacher')
    elif request.user.is_student:
        return redirect('dashboard:student')
    elif request.user.is_parent:
        return redirect('dashboard:parent')
    else:
        # Fallback if user type is not recognized
        messages.error(request, 'Unable to determine your user type. Please contact support.')
        return redirect('core:home')

@login_required
def teacher_dashboard(request):
    """Dashboard for teacher (Patience)"""
    if not request.user.is_teacher:
        return redirect('users:dashboard')
    
    # Dashboard statistics
    total_students = User.objects.filter(user_type='student').count()
    total_materials = Material.objects.filter(uploaded_by=request.user).count()
    total_assignments = Assignment.objects.filter(created_by=request.user).count()
    
    # Recent activities
    recent_materials = Material.objects.filter(uploaded_by=request.user)[:5]
    recent_messages = Message.objects.filter(sender=request.user)[:5]
    
    context = {
        'total_students': total_students,
        'total_materials': total_materials,
        'total_assignments': total_assignments,
        'recent_materials': recent_materials,
        'recent_messages': recent_messages,
    }
    
    return render(request, 'dashboard/teacher.html', context)

@login_required
def student_dashboard(request):
    """Dashboard for students"""
    if not request.user.is_student:
        return redirect('users:dashboard')
    
    # Student progress
    my_assignments = Assignment.objects.filter(assigned_to=request.user)
    my_progress = StudentProgress.objects.filter(student=request.user)
    completed_count = my_progress.filter(completed_at__isnull=False).count()
    
    # Recent activities
    recent_materials = Material.objects.filter(is_active=True)[:5]
    my_chats = ChatRoom.objects.filter(participants=request.user)
    
    context = {
        'my_assignments': my_assignments,
        'total_assignments': my_assignments.count(),
        'completed_assignments': completed_count,
        'completion_rate': (completed_count / my_assignments.count() * 100) if my_assignments.count() > 0 else 0,
        'recent_materials': recent_materials,
        'my_chats': my_chats,
    }
    
    return render(request, 'dashboard/student.html', context)

@login_required
def parent_dashboard(request):
    """Dashboard for parents"""
    if not request.user.is_parent:
        return redirect('users:dashboard')
    
    # Find children (students with this parent's email)
    children = User.objects.filter(parent_email=request.user.email, user_type='student')
    
    # Aggregate children's progress
    total_assignments = 0
    completed_assignments = 0
    
    for child in children:
        child_assignments = Assignment.objects.filter(assigned_to=child).count()
        child_completed = StudentProgress.objects.filter(
            student=child, 
            completed_at__isnull=False
        ).count()
        total_assignments += child_assignments
        completed_assignments += child_completed
    
    context = {
        'children': children,
        'total_assignments': total_assignments,
        'completed_assignments': completed_assignments,
        'completion_rate': (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0,
    }
    
    return render(request, 'dashboard/parent.html', context)


@login_required
def create_material(request):
    """Teacher view to upload new learning material"""
    if not request.user.is_teacher:
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = CreateMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            material.save()
            messages.success(request, 'Material uploaded successfully.')
            return redirect('dashboard:teacher')
    else:
        form = CreateMaterialForm()

    return render(request, 'dashboard/create_material.html', {'form': form})


@login_required
def create_assignment(request):
    """Teacher view to create an assignment from existing material"""
    if not request.user.is_teacher:
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = CreateAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            form.save_m2m()
            messages.success(request, 'Assignment created and assigned to students.')
            return redirect('dashboard:teacher')
    else:
        form = CreateAssignmentForm()

    return render(request, 'dashboard/create_assignment.html', {'form': form})


@login_required
def students_list(request):
    """List all students for the teacher to manage"""
    if not request.user.is_teacher:
        return redirect('users:dashboard')

    User = get_user_model()
    students = User.objects.filter(user_type='student')
    return render(request, 'dashboard/students_list.html', {'students': students})


@login_required
def send_announcement(request):
    """Send a broadcast announcement message to all students or parents"""
    if not request.user.is_teacher:
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            recipient_group = form.cleaned_data['recipient_group']
            # Create a chat room for announcement (teacher-only visible) and post message
            room = ChatRoom.objects.create(name=f"Announcement by {request.user.username}", created_by=request.user, is_group_chat=True)
            # add recipients
            if recipient_group == 'students':
                recipients = get_user_model().objects.filter(user_type='student')
            else:
                recipients = get_user_model().objects.filter(user_type='parent')
            room.participants.add(request.user, *recipients)
            Message.objects.create(room=room, sender=request.user, message_type='text', content=content)
            messages.success(request, 'Announcement sent.')
            return redirect('dashboard:teacher')
    else:
        form = AnnouncementForm()

    return render(request, 'dashboard/send_announcement.html', {'form': form})
