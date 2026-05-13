from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from hub.models import Assignment, Material, Subject


class Command(BaseCommand):
    help = "Seed demo data: subjects, a material, and an assignment"

    def handle(self, *args, **options):
        U = get_user_model()

        teacher = U.objects.filter(user_type="teacher").first()
        student = U.objects.filter(user_type="student").first()

        if not teacher or not student:
            self.stdout.write(
                self.style.WARNING(
                    "Require at least one teacher and one student to seed data."
                )
            )
            return

        math, _ = Subject.objects.get_or_create(
            name="Mathematics",
            defaults={
                "description": "Numbers, algebra, geometry, and more",
                "color_code": "#1e90ff",
            },
        )

        material, _ = Material.objects.get_or_create(
            title="Fractions Basics",
            subject=math,
            defaults={
                "description": "Introductory worksheet on fractions",
                "material_type": "worksheet",
                "difficulty_level": "beginner",
                "grade_level": "4",
                "estimated_time": 30,
                "uploaded_by": teacher,
                "tags": "fractions,math,beginner",
                "is_active": True,
            },
        )

        due = timezone.now() + timezone.timedelta(days=7)
        assignment, _ = Assignment.objects.get_or_create(
            title="Fractions Practice",
            material=material,
            defaults={
                "description": "Complete problems 1-20",
                "created_by": teacher,
                "due_date": due,
                "priority": "medium",
                "max_score": 100,
                "instructions": "Show your work and check answers",
                "submission_format": "PDF or photo of work",
                "is_active": True,
            },
        )
        assignment.assigned_to.add(student)

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded: Mathematics subject, material 'Fractions Basics', and 'Fractions Practice' assignment."
            )
        )
