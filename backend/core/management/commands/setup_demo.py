from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from hub.models import Assignment, Material, Subject


class Command(BaseCommand):
    help = "Create demo users and seed sample data for testing"

    def handle(self, *args, **options):
        User = get_user_model()

        self.stdout.write("🚀 Setting up demo environment...")

        # Create demo teacher
        teacher, created = User.objects.get_or_create(
            username="demo_teacher",
            defaults={
                "email": "teacher@demo.com",
                "first_name": "Demo",
                "last_name": "Teacher",
                "user_type": "teacher",
                "is_staff": True,
                "is_verified": True,
            }
        )
        if created:
            teacher.set_password("demo123")
            teacher.save()
            self.stdout.write(self.style.SUCCESS("✅ Created demo teacher: demo_teacher / demo123"))

        # Create demo student
        student, created = User.objects.get_or_create(
            username="demo_student",
            defaults={
                "email": "student@demo.com",
                "first_name": "Demo",
                "last_name": "Student",
                "user_type": "student",
                "grade_level": "8",
                "parent_email": "parent@demo.com",
                "is_verified": True,
            }
        )
        if created:
            student.set_password("demo123")
            student.save()
            self.stdout.write(self.style.SUCCESS("✅ Created demo student: demo_student / demo123"))

        # Create subjects
        subjects_data = [
            {"name": "Mathematics", "description": "Numbers, algebra, geometry", "color_code": "#1e90ff"},
            {"name": "English", "description": "Reading, writing, literature", "color_code": "#32cd32"},
            {"name": "Science", "description": "Biology, chemistry, physics", "color_code": "#ff6347"},
        ]

        for subj_data in subjects_data:
            subject, _ = Subject.objects.get_or_create(
                name=subj_data["name"],
                defaults=subj_data
            )

        self.stdout.write(self.style.SUCCESS("✅ Created subjects: Math, English, Science"))

        # Create sample materials
        materials_data = [
            {
                "title": "Introduction to Fractions",
                "subject": Subject.objects.get(name="Mathematics"),
                "description": "Learn the basics of fractions with visual examples",
                "material_type": "worksheet",
                "difficulty_level": "beginner",
                "grade_level": "5",
                "estimated_time": 45,
                "uploaded_by": teacher,
                "tags": "fractions,math,beginner",
                "is_active": True,
            },
            {
                "title": "Shakespeare Sonnets",
                "subject": Subject.objects.get(name="English"),
                "description": "Analysis of Shakespeare's most famous sonnets",
                "material_type": "reading",
                "difficulty_level": "intermediate",
                "grade_level": "9",
                "estimated_time": 60,
                "uploaded_by": teacher,
                "tags": "shakespeare,poetry,literature",
                "is_active": True,
            },
            {
                "title": "Photosynthesis Explained",
                "subject": Subject.objects.get(name="Science"),
                "description": "How plants convert sunlight into energy",
                "material_type": "video",
                "difficulty_level": "beginner",
                "grade_level": "6",
                "estimated_time": 30,
                "uploaded_by": teacher,
                "tags": "biology,photosynthesis,plants",
                "is_active": True,
            },
        ]

        for mat_data in materials_data:
            material, _ = Material.objects.get_or_create(
                title=mat_data["title"],
                defaults=mat_data
            )

        self.stdout.write(self.style.SUCCESS("✅ Created sample materials"))

        # Create sample assignments
        assignments_data = [
            {
                "title": "Fractions Worksheet",
                "material": Material.objects.get(title="Introduction to Fractions"),
                "description": "Complete exercises 1-15 on the fractions worksheet",
                "created_by": teacher,
                "due_date": timezone.now() + timezone.timedelta(days=5),
                "priority": "medium",
                "max_score": 100,
                "instructions": "Show all your work. Circle your final answers.",
                "submission_format": "PDF upload or photo",
                "is_active": True,
            },
            {
                "title": "Sonnet Analysis",
                "material": Material.objects.get(title="Shakespeare Sonnets"),
                "description": "Write a 500-word analysis of Sonnet 18",
                "created_by": teacher,
                "due_date": timezone.now() + timezone.timedelta(days=7),
                "priority": "high",
                "max_score": 50,
                "instructions": "Use MLA format. Include quotes from the text.",
                "submission_format": "Word document or Google Doc link",
                "is_active": True,
            },
        ]

        for assign_data in assignments_data:
            assignment, _ = Assignment.objects.get_or_create(
                title=assign_data["title"],
                defaults=assign_data
            )
            assignment.assigned_to.add(student)

        self.stdout.write(self.style.SUCCESS("✅ Created sample assignments"))

        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("🎉 DEMO SETUP COMPLETE!"))
        self.stdout.write("="*50)
        self.stdout.write("\n📚 Demo Accounts:")
        self.stdout.write("   Teacher: demo_teacher / demo123")
        self.stdout.write("   Student: demo_student / demo123")
        self.stdout.write("\n🌐 Test the app at: https://pg-tutoring-hub.onrender.com/")
        self.stdout.write("\n📋 What to test:")
        self.stdout.write("   • Login with both accounts")
        self.stdout.write("   • View materials and assignments")
        self.stdout.write("   • Try the chat feature")
        self.stdout.write("   • Test on mobile devices")
        self.stdout.write("="*50)