from django.db import models
from django.conf import settings

class Subject(models.Model):
    """Subject categories for materials"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color_code = models.CharField(max_length=7, default='#007bff')  # Hex color
    
    def __str__(self):
        return self.name

class Material(models.Model):
    """Educational materials for students"""
    MATERIAL_TYPES = (
        ('worksheet', 'Worksheet'),
        ('test', 'Test'),
        ('assignment', 'Assignment'),
        ('reading', 'Reading Material'),
        ('video', 'Video'),
        ('game', 'Educational Game'),
    )
    
    DIFFICULTY_LEVELS = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    
    # File upload
    file = models.FileField(upload_to='materials/', blank=True, null=True)
    external_link = models.URLField(blank=True)
    
    # Metadata
    grade_level = models.CharField(max_length=20)
    estimated_time = models.IntegerField(help_text="Estimated time in minutes")
    
    # Tracking
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.subject.name})"

class Assignment(models.Model):
    """Assignments given to students"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    
    # Assignment details
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='assignments')
    due_date = models.DateTimeField()
    
    # Tracking
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class StudentProgress(models.Model):
    """Track student progress on materials"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    
    # Progress tracking
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True, help_text="Score out of 100")
    
    # Notes
    teacher_notes = models.TextField(blank=True)
    student_notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('student', 'material')
    
    def __str__(self):
        return f"{self.student.username} - {self.material.title}"
    
    @property
    def is_completed(self):
        return self.completed_at is not None
