#!/usr/bin/env python
import os
import sys

import django

# Add the project directory to the Python path
sys.path.append("/home/obrien-tg/pg_tutoring_hub")

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pg_hub.settings")

# Setup Django
django.setup()

import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from hub.models import (Assignment, AssignmentSubmission, Material,
                        StudentProgress)

User = get_user_model()
student = User.objects.get(username="student1")

# Get all materials
materials = Material.objects.all()

# Create progress records for each material
for material in materials:
    # Check if progress already exists
    progress, created = StudentProgress.objects.get_or_create(
        student=student,
        material=material,
        defaults={
            "status": random.choice(["completed", "in_progress", "not_started"]),
            "score": random.randint(70, 100) if random.random() > 0.3 else None,
            "time_spent_minutes": random.randint(15, 120),
        },
    )

    # Set completion date for completed items
    if progress.status == "completed" and not progress.completed_at:
        progress.completed_at = timezone.now() - timedelta(days=random.randint(1, 5))
        progress.save()

print("✅ Created sample progress data:")
progress_records = StudentProgress.objects.filter(student=student)
for progress in progress_records:
    print(
        f'  • {progress.material.title}: {progress.get_status_display()} - Score: {progress.score or "N/A"}% - Time: {progress.time_spent_minutes}m'
    )

print(f"\n📊 Progress Summary:")
print(f"   Total materials: {progress_records.count()}")
print(f'   Completed: {progress_records.filter(status="completed").count()}')
print(f'   In Progress: {progress_records.filter(status="in_progress").count()}')
print(f'   Not Started: {progress_records.filter(status="not_started").count()}')
