from django.contrib import admin

from .models import Assignment, AssignmentSubmission, Material, StudentProgress, Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "color_code", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "subject",
        "material_type",
        "difficulty_level",
        "grade_level",
        "uploaded_by",
        "is_active",
    )
    list_filter = ("material_type", "difficulty_level", "grade_level", "is_active")
    search_fields = ("title", "description", "tags", "uploaded_by__username")


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "material",
        "created_by",
        "due_date",
        "priority",
        "is_active",
    )
    list_filter = ("priority", "is_active", "due_date")
    search_fields = ("title", "description", "created_by__username")


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "material", "status", "score", "completed_at", "graded_at")
    list_filter = ("status", "completed_at", "graded_at")
    search_fields = ("student__username", "student__email", "material__title")


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "assignment",
        "student",
        "status",
        "grade",
        "numeric_score",
        "revision_requested",
        "graded_by",
        "graded_at",
    )
    list_filter = ("status", "grade", "revision_requested", "graded_at")
    search_fields = (
        "assignment__title",
        "student__username",
        "student__email",
        "teacher_feedback",
        "revision_notes",
    )
