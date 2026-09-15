from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from chat.models import ChatRoom, Message
from hub.models import Assignment, AssignmentSubmission, Material, StudentProgress

from .forms import AnnouncementForm, CreateAssignmentForm, CreateMaterialForm

User = get_user_model()


@login_required
def dashboard_index(request):
    """Redirect users to their appropriate dashboard based on user type"""
    if request.user.is_teacher:
        return redirect("dashboard:teacher")
    elif request.user.is_student:
        return redirect("dashboard:student")
    elif request.user.is_parent:
        return redirect("dashboard:parent")
    else:
        # Fallback if user type is not recognized
        messages.error(
            request, "Unable to determine your user type. Please contact support."
        )
        return redirect("core:home")


@login_required
def teacher_dashboard(request):
    """Dashboard for teacher (Patience)"""
    if not request.user.is_teacher:
        return redirect("users:dashboard")

    # Dashboard statistics
    total_students = User.objects.filter(user_type="student").count()
    total_materials = Material.objects.filter(uploaded_by=request.user).count()
    total_assignments = Assignment.objects.filter(created_by=request.user).count()

    # Recent activities
    recent_materials = Material.objects.filter(uploaded_by=request.user)[:5]
    recent_messages = Message.objects.filter(sender=request.user)[:5]

    context = {
        "total_students": total_students,
        "total_materials": total_materials,
        "total_assignments": total_assignments,
        "recent_materials": recent_materials,
        "recent_messages": recent_messages,
    }

    return render(request, "dashboard/teacher.html", context)


@login_required
def student_dashboard(request):
    """Dashboard for students"""
    if not request.user.is_student:
        return redirect("users:dashboard")

    from datetime import timedelta

    from django.utils import timezone

    my_assignments = list(
        Assignment.objects.filter(
            assigned_to=request.user, is_active=True
        )
        .select_related("material__subject")
        .order_by("due_date")
    )
    submissions = {
        submission.assignment_id: submission
        for submission in AssignmentSubmission.objects.filter(
            student=request.user, assignment_id__in=[a.pk for a in my_assignments]
        )
    }
    next_assignment = next(
        (
            assignment
            for assignment in my_assignments
            if assignment.pk not in submissions
            or submissions[assignment.pk].revision_requested
        ),
        None,
    )

    my_progress = list(
        StudentProgress.objects.filter(student=request.user).select_related(
            "material__subject"
        )
    )
    completed_count = sum(
        1 for progress in my_progress if progress.completed_at is not None
    )
    graded_submissions = list(
        AssignmentSubmission.objects.filter(
            student=request.user, status="graded"
        )
        .select_related("assignment__material__subject")
        .order_by("-graded_at")[:3]
    )

    mastery_by_subject = {}
    for progress in my_progress:
        subject = progress.material.subject
        subject_data = mastery_by_subject.setdefault(
            subject.pk,
            {"name": subject.name, "color": subject.color_code, "total": 0, "points": 0},
        )
        subject_data["total"] += 1
        subject_data["points"] += progress.completion_percentage
    subject_mastery = [
        {
            **subject_data,
            "percentage": round(subject_data["points"] / subject_data["total"]),
        }
        for subject_data in mastery_by_subject.values()
    ][:4]

    today = timezone.localdate()
    week_start = today - timedelta(days=6)
    weekly_effort = [
        {"date": week_start + timedelta(days=offset), "minutes": 0}
        for offset in range(7)
    ]
    for progress in my_progress:
        if progress.started_at and progress.started_at.date() >= week_start:
            day_offset = (progress.started_at.date() - week_start).days
            weekly_effort[day_offset]["minutes"] += progress.time_spent_minutes

    # Recent activities
    recent_materials = Material.objects.filter(is_active=True).select_related(
        "subject"
    )[:5]
    my_chats = ChatRoom.objects.filter(participants=request.user).prefetch_related(
        "messages"
    )[:5]

    context = {
        "my_assignments": my_assignments,
        "next_assignment": next_assignment,
        "next_assignment_submission": (
            submissions.get(next_assignment.pk) if next_assignment else None
        ),
        "graded_submissions": graded_submissions,
        "subject_mastery": subject_mastery,
        "weekly_effort": weekly_effort,
        "total_assignments": len(my_assignments),
        "completed_assignments": completed_count,
        "completion_rate": (
            (completed_count / len(my_assignments) * 100)
            if my_assignments
            else 0
        ),
        "recent_materials": recent_materials,
        "my_chats": my_chats,
    }

    return render(request, "dashboard/student.html", context)


@login_required
def parent_dashboard(request):
    """Dashboard for parents"""
    if not request.user.is_parent:
        return redirect("users:dashboard")

    # Find children (students with this parent's email)
    children = User.objects.filter(parent_email=request.user.email, user_type="student")

    # Aggregate children's progress
    total_assignments = 0
    completed_assignments = 0

    for child in children:
        child_assignments = Assignment.objects.filter(assigned_to=child).count()
        child_completed = StudentProgress.objects.filter(
            student=child, completed_at__isnull=False
        ).count()
        total_assignments += child_assignments
        completed_assignments += child_completed

    context = {
        "children": children,
        "total_assignments": total_assignments,
        "completed_assignments": completed_assignments,
        "completion_rate": (
            (completed_assignments / total_assignments * 100)
            if total_assignments > 0
            else 0
        ),
    }

    return render(request, "dashboard/parent.html", context)


@login_required
def create_material(request):
    """Teacher view to upload new learning material"""
    if not request.user.is_teacher:
        return redirect("users:dashboard")

    if request.method == "POST":
        form = CreateMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            material.save()
            messages.success(request, "Material uploaded successfully.")
            return redirect("dashboard:teacher")
    else:
        form = CreateMaterialForm()

    return render(request, "dashboard/create_material.html", {"form": form})


@login_required
def create_assignment(request):
    """Teacher view to create an assignment from existing material"""
    if not request.user.is_teacher:
        return redirect("users:dashboard")

    if request.method == "POST":
        form = CreateAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            form.save_m2m()
            messages.success(request, "Assignment created and assigned to students.")
            return redirect("dashboard:teacher")
    else:
        form = CreateAssignmentForm()

    return render(request, "dashboard/create_assignment.html", {"form": form})


@login_required
def students_list(request):
    """List all students for the teacher to manage"""
    if not request.user.is_teacher:
        return redirect("users:dashboard")

    User = get_user_model()
    students = User.objects.filter(user_type="student")
    return render(request, "dashboard/students_list.html", {"students": students})


@login_required
def send_announcement(request):
    """Send a broadcast announcement message to all students or parents"""
    if not request.user.is_teacher:
        return redirect("users:dashboard")

    if request.method == "POST":
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            recipient_group = form.cleaned_data["recipient_group"]
            # Create a chat room for announcement (teacher-only visible) and post message
            room = ChatRoom.objects.create(
                name=f"Announcement by {request.user.username}",
                created_by=request.user,
                is_group_chat=True,
            )
            # add recipients
            if recipient_group == "students":
                recipients = get_user_model().objects.filter(user_type="student")
            else:
                recipients = get_user_model().objects.filter(user_type="parent")
            room.participants.add(request.user, *recipients)
            Message.objects.create(
                room=room, sender=request.user, message_type="text", content=content
            )
            messages.success(request, "Announcement sent.")
            return redirect("dashboard:teacher")
    else:
        form = AnnouncementForm()

    return render(request, "dashboard/send_announcement.html", {"form": form})


@login_required
def firebase_settings(request):
    """View for Firebase integration settings page"""
    # Allow all authenticated users to view Firebase settings for now
    return render(request, "firebase_settings.html")
