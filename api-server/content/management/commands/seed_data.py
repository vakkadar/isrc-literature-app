from django.core.management.base import BaseCommand
from content.models import Author, Subject, Tag, ContentItem


class Command(BaseCommand):
    help = "Seed the database with sample content for testing"

    def handle(self, *args, **options):
        authors = [
            Author.objects.get_or_create(
                name="Swami Vivekananda",
                defaults={"description": "Indian Hindu monk and philosopher"},
            )[0],
            Author.objects.get_or_create(
                name="Paramahansa Yogananda",
                defaults={"description": "Indian monk and yogi"},
            )[0],
            Author.objects.get_or_create(
                name="Sri Aurobindo",
                defaults={"description": "Indian philosopher, yogi, and poet"},
            )[0],
        ]

        subjects = [
            Subject.objects.get_or_create(
                name="Vedanta",
                defaults={"description": "Hindu philosophical tradition"},
            )[0],
            Subject.objects.get_or_create(
                name="Yoga",
                defaults={"description": "Spiritual and physical practices"},
            )[0],
            Subject.objects.get_or_create(
                name="Meditation",
                defaults={"description": "Contemplative practices"},
            )[0],
        ]

        tags_list = ["lecture", "discourse", "bhajan", "guided", "philosophy", "practice"]
        tags = []
        for tag_name in tags_list:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)

        sample_items = [
            {
                "title": "Karma Yoga - Lecture 1",
                "author": authors[0],
                "subject": subjects[0],
                "year": 2020,
                "content_type": "audio",
                "drive_file_id": "sample_drive_id_001",
                "file_hash": "abc123hash001",
                "duration_seconds": 3600,
                "file_size_bytes": 36_000_000,
                "description": "Introduction to the path of selfless action",
                "tags_list": [tags[0], tags[4]],
            },
            {
                "title": "Raja Yoga - The Science of Mind",
                "author": authors[0],
                "subject": subjects[1],
                "year": 2020,
                "content_type": "audio",
                "drive_file_id": "sample_drive_id_002",
                "file_hash": "abc123hash002",
                "duration_seconds": 2700,
                "file_size_bytes": 27_000_000,
                "description": "Exploring the yoga of mental discipline",
                "tags_list": [tags[0], tags[5]],
            },
            {
                "title": "Autobiography of a Yogi - Chapter Reading",
                "author": authors[1],
                "subject": subjects[1],
                "year": 2019,
                "content_type": "audio",
                "drive_file_id": "sample_drive_id_003",
                "file_hash": "abc123hash003",
                "duration_seconds": 4500,
                "file_size_bytes": 45_000_000,
                "description": "Audio reading from the spiritual classic",
                "tags_list": [tags[1], tags[4]],
            },
            {
                "title": "The Life Divine - Discourse",
                "author": authors[2],
                "subject": subjects[0],
                "year": 2021,
                "content_type": "audio",
                "drive_file_id": "sample_drive_id_004",
                "file_hash": "abc123hash004",
                "duration_seconds": 5400,
                "file_size_bytes": 54_000_000,
                "description": "Discourse on Sri Aurobindo's magnum opus",
                "tags_list": [tags[1], tags[4]],
            },
            {
                "title": "Guided Meditation - Inner Peace",
                "author": authors[1],
                "subject": subjects[2],
                "year": 2022,
                "content_type": "audio",
                "drive_file_id": "sample_drive_id_005",
                "file_hash": "abc123hash005",
                "duration_seconds": 1800,
                "file_size_bytes": 18_000_000,
                "description": "A guided meditation session for inner peace",
                "tags_list": [tags[3], tags[5]],
            },
        ]

        for item_data in sample_items:
            item_tags = item_data.pop("tags_list")
            item, created = ContentItem.objects.get_or_create(
                title=item_data["title"],
                defaults=item_data,
            )
            if created:
                item.tags.set(item_tags)
                self.stdout.write(self.style.SUCCESS(f"Created: {item.title}"))
            else:
                self.stdout.write(f"Already exists: {item.title}")

        self.stdout.write(self.style.SUCCESS("\nSeed data loaded successfully!"))
