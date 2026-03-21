from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command


FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "fixtures"

FIXTURE_ORDER = [
    "authors.json",
    "subjects.json",
    "tags.json",
    "content_items.json",
]


class Command(BaseCommand):
    help = "Import content data from JSON fixtures (for syncing between SQLite and Postgres)"

    def handle(self, *args, **options):
        if not FIXTURES_DIR.exists():
            self.stderr.write(self.style.ERROR(f"Fixtures directory not found: {FIXTURES_DIR}"))
            return

        for fixture_file in FIXTURE_ORDER:
            path = FIXTURES_DIR / fixture_file
            if path.exists():
                call_command("loaddata", str(path), verbosity=1)
                self.stdout.write(f"  Loaded {fixture_file}")
            else:
                self.stdout.write(self.style.WARNING(f"  Skipped {fixture_file} (not found)"))

        self.stdout.write(self.style.SUCCESS("\nFixtures imported successfully!"))
