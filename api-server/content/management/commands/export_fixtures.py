import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.serializers import serialize

from content.models import Author, Subject, Tag, ContentItem


FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "fixtures"


class Command(BaseCommand):
    help = "Export content data as JSON fixtures (for syncing between SQLite and Postgres)"

    def handle(self, *args, **options):
        FIXTURES_DIR.mkdir(exist_ok=True)

        models = [
            ("authors", Author),
            ("subjects", Subject),
            ("tags", Tag),
            ("content_items", ContentItem),
        ]

        for name, model in models:
            data = serialize("json", model.objects.all(), indent=2)
            path = FIXTURES_DIR / f"{name}.json"
            path.write_text(data)
            count = model.objects.count()
            self.stdout.write(f"  Exported {count} {name} -> {path.name}")

        self.stdout.write(self.style.SUCCESS("\nFixtures exported to api-server/fixtures/"))
