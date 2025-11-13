from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Validate database connectivity and media/static storage writability"

    def handle(self, *args, **options):
        User = get_user_model()

        self.stdout.write("\n== Storage & Database Diagnostics ==")

        # Database check
        try:
            user_count = User.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f"DB OK: Users table reachable (count={user_count})")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"DB ERROR: {e}"))

        # Media directory check
        media_root: Path = Path(settings.MEDIA_ROOT)
        media_root.mkdir(parents=True, exist_ok=True)
        test_file = media_root / "diagnostics_write_test.txt"
        try:
            test_file.write_text("storage check: ok", encoding="utf-8")
            self.stdout.write(
                self.style.SUCCESS(f"MEDIA OK: Writeable at {media_root}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"MEDIA ERROR: {e}"))
        finally:
            try:
                if test_file.exists():
                    test_file.unlink()
            except Exception:
                pass

        # Static root notice (collected in production)
        static_root = getattr(settings, "STATIC_ROOT", None)
        if static_root:
            self.stdout.write(f"STATIC ROOT: {static_root}")
        else:
            self.stdout.write("STATIC ROOT: not configured (ok for dev)")

        self.stdout.write(self.style.SUCCESS("Diagnostics complete."))
