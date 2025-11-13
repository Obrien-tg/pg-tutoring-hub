import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Assignment, AssignmentSubmission, Material, StudentProgress


def materials_list(request):
    """List all available materials"""
    materials = Material.objects.filter(is_active=True)
    return render(request, "hub/materials_list.html", {"materials": materials})


def material_detail(request, pk):
    """Show details of a specific material"""
    material = get_object_or_404(Material, pk=pk)
    return render(request, "hub/material_detail.html", {"material": material})


def assignments_list(request):
    """List student assignments"""
    # If logged in, show assigned assignments; otherwise show all
    if request.user.is_authenticated and request.user.user_type == "student":
        assignments = Assignment.objects.filter(assigned_to=request.user)
    else:
        assignments = Assignment.objects.all()
    return render(request, "hub/assignments_list.html", {"assignments": assignments})


def progress_view(request):
    """Show student progress with enhanced analytics"""
    if request.user.is_authenticated and request.user.user_type == "student":
        progress_list = StudentProgress.objects.filter(
            student=request.user
        ).select_related("material__subject")

        # Calculate progress statistics
        total_count = progress_list.count()
        completed_count = progress_list.filter(status="completed").count()
        in_progress_count = progress_list.filter(status="in_progress").count()
        not_started_count = progress_list.filter(status="not_started").count()

        # Calculate overall completion percentage
        overall_completion = (
            (completed_count / total_count * 100) if total_count > 0 else 0
        )

        # Calculate average score
        scored_progress = progress_list.filter(score__isnull=False)
        average_score = (
            scored_progress.aggregate(avg_score=models.Avg("score"))["avg_score"] or 0
        )

        # Calculate best score
        best_score = scored_progress.aggregate(max_score=models.Max("score"))[
            "max_score"
        ]

        # Calculate total study time
        total_study_time = (
            progress_list.aggregate(total_time=models.Sum("time_spent_minutes"))[
                "total_time"
            ]
            or 0
        )

        # Calculate study streak (simplified - consecutive days with activity)
        from datetime import datetime, timedelta

        today = timezone.now().date()
        study_streak = 0
        for i in range(30):  # Check last 30 days
            check_date = today - timedelta(days=i)
            if progress_list.filter(
                models.Q(started_at__date=check_date)
                | models.Q(completed_at__date=check_date)
            ).exists():
                study_streak += 1
            else:
                break

        # This week's completed materials
        week_ago = timezone.now() - timedelta(days=7)
        this_week_completed = progress_list.filter(completed_at__gte=week_ago).count()

        context = {
            "progress_list": progress_list,
            "total_count": total_count,
            "completed_count": completed_count,
            "in_progress_count": in_progress_count,
            "not_started_count": not_started_count,
            "overall_completion": round(overall_completion, 1),
            "average_score": average_score,
            "best_score": best_score,
            "total_study_time": total_study_time,
            "study_streak": study_streak,
            "this_week_completed": this_week_completed,
        }
    else:
        context = {
            "progress_list": StudentProgress.objects.none(),
            "total_count": 0,
            "completed_count": 0,
            "in_progress_count": 0,
            "not_started_count": 0,
            "overall_completion": 0,
            "average_score": 0,
            "best_score": None,
            "total_study_time": 0,
            "study_streak": 0,
            "this_week_completed": 0,
        }

    return render(request, "hub/progress.html", context)


@login_required
def submit_assignment(request, assignment_id):
    """Submit assignment with file upload and text"""
    assignment = get_object_or_404(Assignment, pk=assignment_id)

    # Check if user is authorized to submit this assignment
    if (
        request.user.user_type != "student"
        or request.user not in assignment.assigned_to.all()
    ):
        messages.error(request, "You are not authorized to submit this assignment.")
        return redirect("assignments_list")

    # Check if already submitted
    existing_submission = AssignmentSubmission.objects.filter(
        assignment=assignment, student=request.user
    ).first()

    if request.method == "POST":
        submission_text = request.POST.get("submission_text", "").strip()
        submission_notes = request.POST.get("submission_notes", "").strip()
        submission_file = request.FILES.get("submission_file")

        # Validate that at least one form of submission is provided
        if not submission_text and not submission_file:
            messages.error(
                request, "Please provide either text submission or upload a file."
            )
            return render(
                request,
                "hub/submit_assignment.html",
                {"assignment": assignment, "existing_submission": existing_submission},
            )

        try:
            if existing_submission:
                # Update existing submission
                existing_submission.submission_text = submission_text
                existing_submission.submission_notes = submission_notes
                if submission_file:
                    existing_submission.submission_file = submission_file
                existing_submission.status = "submitted"
                existing_submission.save()
                messages.success(
                    request, "Your assignment has been updated successfully!"
                )
            else:
                # Create new submission
                submission = AssignmentSubmission.objects.create(
                    assignment=assignment,
                    student=request.user,
                    submission_text=submission_text,
                    submission_notes=submission_notes,
                    submission_file=submission_file,
                    status="submitted",
                )
                messages.success(
                    request, "Your assignment has been submitted successfully!"
                )

            return redirect("assignments_list")

        except Exception as e:
            messages.error(request, f"Error submitting assignment: {str(e)}")

    return render(
        request,
        "hub/submit_assignment.html",
        {"assignment": assignment, "existing_submission": existing_submission},
    )


def assignment_detail(request, assignment_id):
    """View assignment details"""
    assignment = get_object_or_404(Assignment, pk=assignment_id)

    # Check if user has submitted this assignment
    submission = None
    if request.user.is_authenticated and request.user.user_type == "student":
        submission = AssignmentSubmission.objects.filter(
            assignment=assignment, student=request.user
        ).first()

    context = {
        "assignment": assignment,
        "submission": submission,
        "can_submit": (
            request.user.is_authenticated
            and request.user.user_type == "student"
            and request.user in assignment.assigned_to.all()
        ),
    }

    return render(request, "hub/assignment_detail.html", context)
