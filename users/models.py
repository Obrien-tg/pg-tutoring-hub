from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
import os

def validate_image_size(image):
    """Validate that image is not too large"""
    file_size = image.file.size
    limit_mb = 5
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError(f"Image file too large ( > {limit_mb}MB )")

def profile_picture_path(instance, filename):
    """Generate upload path for profile pictures"""
    # Get file extension
    ext = filename.split('.')[-1]
    # Rename file to user ID
    filename = f"user_{instance.id}_profile.{ext}"
    return os.path.join('profile_pics', filename)

class CustomUser(AbstractUser):
    """Custom user model with role-based permissions"""
    USER_TYPES = (
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('teacher', 'Teacher'),
    )
    
    # Phone number validator
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        help_text="Enter phone number in format: +1234567890"
    )
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to=profile_picture_path, 
        blank=True, 
        null=True,
        validators=[
            validate_image_size,
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
        ],
        help_text="Upload a profile picture (max 5MB, JPG/PNG/GIF only)"
    )
    
    # Student-specific fields
    grade_level = models.CharField(max_length=20, blank=True)
    parent_email = models.EmailField(blank=True)
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True
    )
    
    # Account status
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=['user_type']),
            models.Index(fields=['is_verified']),
        ]
    
    def clean(self):
        """Custom validation"""
        super().clean()
        
        # Validate student-specific fields
        if self.user_type == 'student':
            if not self.grade_level:
                raise ValidationError({'grade_level': 'Grade level is required for students.'})
            if not self.parent_email:
                raise ValidationError({'parent_email': 'Parent email is required for students.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def is_student(self):
        return self.user_type == 'student'
    
    @property
    def is_parent(self):
        return self.user_type == 'parent'
    
    @property
    def is_teacher(self):
        return self.user_type == 'teacher'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
