from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0002_alter_discovery_source"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="lineage_group",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "— Not in crawler —"),
                    ("A_BABUJI", "A — Babuji + direct disciples"),
                    ("B_LALAJI_DIRECT", "B — Lalaji's direct disciples"),
                    ("C_LINEAGE", "C — Lalaji's predecessor lineage"),
                ],
                default="",
                help_text="Group this person belongs to for the crawler. Blank = not crawled.",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="crawl_active",
            field=models.BooleanField(
                default=True,
                help_text="Include in crawler runs",
            ),
        ),
    ]
