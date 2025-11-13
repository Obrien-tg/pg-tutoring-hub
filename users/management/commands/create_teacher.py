from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create a teacher account for PG Tutoring Hub"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            required=True,
            help="Username for the teacher account",
        )
        parser.add_argument(
            "--email", type=str, required=True, help="Email for the teacher account"
        )
        parser.add_argument(
            "--password",
            type=str,
            required=True,
            help="Password for the teacher account",
        )
        parser.add_argument(
            "--first-name", type=str, default="", help="First name of the teacher"
        )
        parser.add_argument(
            "--last-name", type=str, default="", help="Last name of the teacher"
        )

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]
        first_name = options["first_name"]
        last_name = options["last_name"]

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'User with username "{username}" already exists.')
            )
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'User with email "{email}" already exists.')
            )
            return

        try:
            # Create teacher user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type="teacher",
                is_staff=True,  # Teachers can access admin
                is_verified=True,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created teacher account: {username} ({email})"
                )
            )

        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f"Validation error: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating user: {e}"))
