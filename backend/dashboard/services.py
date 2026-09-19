from datetime import timedelta

from django.utils import timezone

from chat.models import ChatRoom
from hub.models import Assignment, AssignmentSubmission, Material, StudentProgress

def build_student_dashboard(student):
    """Build the shared student dashboard data used by HTML and API clients."""
    assignments = list(
        Assignment.objects.filter(assigned_to=student, is_active=True)
        .select_related("material__subject")
        .order_by("due_date")
    )
    assignment_ids = [assignment.pk for assignment in assignments]
    submissions = {
        submission.assignment_id: submission
        for submission in AssignmentSubmission.objects.filter(
            student=student,
            assignment_id__in=assignment_ids,
        )
    }
    next_assignment = next(
        (
            assignment
            for assignment in assignments
            if assignment.pk not in submissions
            or submissions[assignment.pk].revision_requested
        ),
        None,
    )

    progress = list(
        StudentProgress.objects.filter(student=student).select_related(
            "material__subject"
        )
    )
    active_completed_count = (
        StudentProgress.objects.filter(
            student=student,
            assignment_id__in=assignment_ids,
            completed_at__isnull=False,
        ).count()
        if assignment_ids
        else 0
    )
    graded_submissions = list(
        AssignmentSubmission.objects.filter(student=student, status="graded")
        .select_related("assignment__material__subject")
        .order_by("-graded_at")[:3]
    )

    mastery_by_subject = {}
    for record in progress:
        subject = record.material.subject
        subject_data = mastery_by_subject.setdefault(
            subject.pk,
            {
                "name": subject.name,
                "color": subject.color_code,
                "total": 0,
                "points": 0,
            },
        )
        subject_data["total"] += 1
        subject_data["points"] += record.completion_percentage
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
        {"date": week_start + timedelta(days=index), "minutes": 0}
        for index in range(7)
    ]
    for record in progress:
        if record.started_at:
            local_date = timezone.localtime(record.started_at).date()
            if local_date >= week_start:
                weekly_effort[(local_date - week_start).days]["minutes"] += (
                    record.time_spent_minutes
                )

    recent_materials = Material.objects.filter(is_active=True).select_related(
        "subject"
    )[:5]
    my_chats = ChatRoom.objects.filter(participants=student)[:5]

    return {
        "my_assignments": assignments,
        "next_assignment": next_assignment,
        "next_assignment_submission": (
            submissions.get(next_assignment.pk) if next_assignment else None
        ),
        "graded_submissions": graded_submissions,
        "subject_mastery": subject_mastery,
        "weekly_effort": weekly_effort,
        "my_progress": progress,
        "total_assignments": len(assignments),
        "completed_assignments": active_completed_count,
        "completion_rate": (
            active_completed_count / len(assignments) * 100 if assignments else 0
        ),
        "recent_materials": recent_materials,
        "my_chats": my_chats,
    }
