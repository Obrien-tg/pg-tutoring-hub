import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (FileExtensionValidator, MaxValueValidator,
                                    MinValueValidator)
from django.db import models


def validate_file_size(file):
    """Validate that file is not too large"""
    file_size = file.file.size
    limit_mb = 50  # 50MB limit for educational materials
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError(f"File too large ( > {limit_mb}MB )")


def material_upload_path(instance, filename):
    """Generate organized upload path for materials"""
    # Get file extension
    ext = filename.split(".")[-1]
    # Create organized path: materials/subject/year-month/filename
    from datetime import datetime

    date_path = datetime.now().strftime("%Y-%m")
    subject_name = instance.subject.name.lower().replace(" ", "_")

    # Sanitize filename
    safe_filename = "".join(
        c for c in filename if c.isalnum() or c in (" ", "-", "_", ".")
    ).rstrip()

    return os.path.join("materials", subject_name, date_path, safe_filename)


class Subject(models.Model):
    """Subject categories for materials"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color_code = models.CharField(
        max_length=7, default="#007bff", help_text="Hex color code (e.g., #FF5733)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def clean(self):
        """Validate color code format"""
        if not self.color_code.startswith("#") or len(self.color_code) != 7:
            raise ValidationError(
                {"color_code": "Color code must be in format #RRGGBB"}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Material(models.Model):
    """Educational materials for students"""

    MATERIAL_TYPES = (
        ("worksheet", "Worksheet"),
        ("test", "Test"),
        ("assignment", "Assignment"),
        ("reading", "Reading Material"),
        ("video", "Video"),
        ("audio", "Audio"),
        ("presentation", "Presentation"),
        ("game", "Educational Game"),
        ("reference", "Reference Material"),
    )

    DIFFICULTY_LEVELS = (
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    )

    GRADE_LEVELS = (
        ("k", "Kindergarten"),
        ("1", "Grade 1"),
        ("2", "Grade 2"),
        ("3", "Grade 3"),
        ("4", "Grade 4"),
        ("5", "Grade 5"),
        ("6", "Grade 6"),
        ("7", "Grade 7"),
        ("8", "Grade 8"),
        ("9", "Grade 9"),
        ("10", "Grade 10"),
        ("11", "Grade 11"),
        ("12", "Grade 12"),
        ("university", "University Level"),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="materials"
    )
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)

    # File upload with validation
    file = models.FileField(
        upload_to=material_upload_path,
        blank=True,
        null=True,
        validators=[
            validate_file_size,
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf",
                    "doc",
                    "docx",
                    "ppt",
                    "pptx",
                    "xls",
                    "xlsx",
                    "jpg",
                    "jpeg",
                    "png",
                    "gif",
                    "svg",
                    "mp4",
                    "avi",
                    "mov",
                    "wmv",
                    "mp3",
                    "wav",
                    "ogg",
                    "zip",
                    "rar",
                    "txt",
                ]
            ),
        ],
        help_text="Upload educational material (max 50MB)",
    )
    external_link = models.URLField(blank=True, help_text="External resource link")

    # Metadata
    grade_level = models.CharField(max_length=20, choices=GRADE_LEVELS)
    estimated_time = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Estimated time in minutes (1-1440)",
    )

    # Tags for better organization
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated tags (e.g., algebra, fractions, beginner)",
    )

    # Tracking
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_materials",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Material"
        verbose_name_plural = "Materials"
        indexes = [
            models.Index(fields=["subject", "grade_level"]),
            models.Index(fields=["material_type", "difficulty_level"]),
            models.Index(fields=["is_active", "created_at"]),
        ]

    def clean(self):
        """Custom validation"""
        if not self.file and not self.external_link:
            raise ValidationError("Either file upload or external link is required.")

        if self.file and self.external_link:
            raise ValidationError(
                "Provide either file upload OR external link, not both."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.subject.name})"

    @property
    def file_size_mb(self):
        """Return file size in MB"""
        if self.file:
            return round(self.file.size / (1024 * 1024), 2)
        return 0

    @property
    def file_extension(self):
        """Return file extension"""
        if self.file:
            return os.path.splitext(self.file.name)[1][1:].upper()
        return None


class Assignment(models.Model):
    """Assignments given to students"""

    PRIORITY_LEVELS = (
        ("low", "Low Priority"),
        ("medium", "Medium Priority"),
        ("high", "High Priority"),
        ("urgent", "Urgent"),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    material = models.ForeignKey(
        Material, on_delete=models.CASCADE, related_name="assignments"
    )

    # Assignment details
    assigned_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="assignments",
        limit_choices_to={"user_type": "student"},
    )
    due_date = models.DateTimeField()
    priority = models.CharField(
        max_length=10, choices=PRIORITY_LEVELS, default="medium"
    )
    max_score = models.PositiveIntegerField(
        default=100, validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )

    # Instructions and requirements
    instructions = models.TextField(
        blank=True, help_text="Detailed instructions for students"
    )
    submission_format = models.CharField(
        max_length=200,
        blank=True,
        help_text="Expected submission format (e.g., PDF, handwritten, online quiz)",
    )

    # Tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_assignments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["due_date", "-created_at"]
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"
        indexes = [
            models.Index(fields=["due_date", "is_active"]),
            models.Index(fields=["created_by", "created_at"]),
        ]

    def clean(self):
        """Custom validation"""
        from django.utils import timezone

        if self.due_date and self.due_date <= timezone.now():
            raise ValidationError({"due_date": "Due date must be in the future."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """Check if assignment is overdue"""
        from django.utils import timezone

        return self.due_date < timezone.now()

    @property
    def days_until_due(self):
        """Calculate days until due date"""
        from django.utils import timezone

        if self.due_date > timezone.now():
            return (self.due_date.date() - timezone.now().date()).days
        return 0


class StudentProgress(models.Model):
    """Track student progress on materials"""

    STATUS_CHOICES = (
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("needs_review", "Needs Review"),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": "student"},
        related_name="progress_records",
    )
    material = models.ForeignKey(
        Material, on_delete=models.CASCADE, related_name="progress_records"
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="progress_records",
    )

    # Progress tracking
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="not_started"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score as percentage (0-100)",
    )

    # Time tracking
    time_spent_minutes = models.PositiveIntegerField(
        default=0, help_text="Total time spent in minutes"
    )

    # Notes and feedback
    teacher_notes = models.TextField(blank=True)
    student_notes = models.TextField(blank=True)
    teacher_feedback = models.TextField(blank=True)

    # Submission tracking
    submission_file = models.FileField(
        upload_to="submissions/",
        blank=True,
        null=True,
        validators=[
            validate_file_size,
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "jpg", "jpeg", "png"]
            ),
        ],
    )
    submission_text = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    # Grading
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="graded_submissions",
        limit_choices_to={"user_type": "teacher"},
    )

    class Meta:
        unique_together = ("student", "material")
        verbose_name = "Student Progress"
        verbose_name_plural = "Student Progress"
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["material", "completed_at"]),
        ]

    def clean(self):
        """Custom validation"""
        if self.completed_at and self.completed_at < self.started_at:
            raise ValidationError(
                {"completed_at": "Completion date cannot be before start date."}
            )

        if self.score is not None and (self.score < 0 or self.score > 100):
            raise ValidationError({"score": "Score must be between 0 and 100."})

    def save(self, *args, **kwargs):
        # Auto-update status based on completion
        if self.completed_at and self.status == "not_started":
            self.status = "completed"
        elif not self.completed_at and self.status == "completed":
            self.status = "in_progress"

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.material.title} ({self.get_status_display()})"

    @property
    def is_completed(self):
        return self.completed_at is not None

    @property
    def completion_percentage(self):
        """Calculate completion percentage based on various factors"""
        if self.is_completed:
            return 100
        elif self.status == "in_progress":
            return 50
        return 0

    @property
    def grade_letter(self):
        """Convert numeric score to letter grade"""
        if self.score is None:
            return None

        if self.score >= 90:
            return "A"
        elif self.score >= 80:
            return "B"
        elif self.score >= 70:
            return "C"
        elif self.score >= 60:
            return "D"
        else:
            return "F"


class AssignmentSubmission(models.Model):
    """Student submissions for assignments"""

    SUBMISSION_STATUS = (
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("graded", "Graded"),
        ("returned", "Returned for Revision"),
    )

    GRADE_CHOICES = (
        ("A+", "A+ (97-100%)"),
        ("A", "A (93-96%)"),
        ("A-", "A- (90-92%)"),
        ("B+", "B+ (87-89%)"),
        ("B", "B (83-86%)"),
        ("B-", "B- (80-82%)"),
        ("C+", "C+ (77-79%)"),
        ("C", "C (73-76%)"),
        ("C-", "C- (70-72%)"),
        ("D", "D (60-69%)"),
        ("F", "F (Below 60%)"),
    )

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": "student"},
        related_name="assignment_submissions",
    )

    # Submission content
    submission_file = models.FileField(
        upload_to="submissions/%Y/%m/",
        blank=True,
        null=True,
        validators=[
            validate_file_size,
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "jpg", "jpeg", "png", "txt"]
            ),
        ],
        help_text="Upload your completed assignment (max 50MB)",
    )
    submission_text = models.TextField(
        blank=True, help_text="Type your answer here if no file upload needed"
    )
    submission_notes = models.TextField(
        blank=True, help_text="Any additional notes or questions for your teacher"
    )

    # Submission tracking
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=SUBMISSION_STATUS, default="submitted"
    )

    # Grading
    grade = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    numeric_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score out of 100",
    )

    # Teacher feedback
    teacher_feedback = models.TextField(
        blank=True, help_text="Feedback and comments from teacher"
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="graded_assignment_submissions",
        limit_choices_to={"user_type": "teacher"},
    )
    graded_at = models.DateTimeField(null=True, blank=True)

    # Revision system
    revision_requested = models.BooleanField(default=False)
    revision_notes = models.TextField(blank=True, help_text="What needs to be improved")

    class Meta:
        unique_together = ("assignment", "student")
        ordering = ["-submitted_at"]
        verbose_name = "Assignment Submission"
        verbose_name_plural = "Assignment Submissions"
        indexes = [
            models.Index(fields=["student", "submitted_at"]),
            models.Index(fields=["assignment", "status"]),
            models.Index(fields=["graded_by", "graded_at"]),
        ]

    def clean(self):
        """Custom validation"""
        if not self.submission_file and not self.submission_text:
            raise ValidationError("Either file upload or text submission is required.")

        if self.numeric_score and not self.grade:
            # Auto-assign letter grade based on numeric score
            if self.numeric_score >= 97:
                self.grade = "A+"
            elif self.numeric_score >= 93:
                self.grade = "A"
            elif self.numeric_score >= 90:
                self.grade = "A-"
            elif self.numeric_score >= 87:
                self.grade = "B+"
            elif self.numeric_score >= 83:
                self.grade = "B"
            elif self.numeric_score >= 80:
                self.grade = "B-"
            elif self.numeric_score >= 77:
                self.grade = "C+"
            elif self.numeric_score >= 73:
                self.grade = "C"
            elif self.numeric_score >= 70:
                self.grade = "C-"
            elif self.numeric_score >= 60:
                self.grade = "D"
            else:
                self.grade = "F"

    def save(self, *args, **kwargs):
        # Update grading timestamp when grade is added
        if self.grade and not self.graded_at:
            from django.utils import timezone

            self.graded_at = timezone.now()
            self.status = "graded"

        # Update status when revision is requested
        if self.revision_requested and self.status != "returned":
            self.status = "returned"

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

    @property
    def is_late(self):
        """Check if submission was after due date"""
        return self.submitted_at > self.assignment.due_date

    @property
    def days_late(self):
        """Calculate how many days late the submission was"""
        if not self.is_late:
            return 0
        delta = self.submitted_at.date() - self.assignment.due_date.date()
        return delta.days

    @property
    def file_extension(self):
        """Return file extension of submitted file"""
        if self.submission_file:
            return os.path.splitext(self.submission_file.name)[1][1:].upper()
        return None

    @property
    def file_size_mb(self):
        """Return file size in MB"""
        if self.submission_file:
            return round(self.submission_file.size / (1024 * 1024), 2)
        return 0
