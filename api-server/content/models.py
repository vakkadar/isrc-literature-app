from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel
from wagtail.search import index


@register_snippet
class Author(index.Indexed, models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    search_fields = [
        index.SearchField("name"),
    ]

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
    ]

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


@register_snippet
class Subject(index.Indexed, models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    search_fields = [
        index.SearchField("name"),
    ]

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
    ]

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


@register_snippet
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    panels = [
        FieldPanel("name"),
    ]

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


@register_snippet
class ContentItem(index.Indexed, models.Model):
    class ContentType(models.TextChoices):
        AUDIO = "audio", "Audio"
        PDF = "pdf", "PDF"

    title = models.CharField(max_length=500)
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="content_items"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="content_items"
    )
    year = models.PositiveIntegerField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="content_items")
    content_type = models.CharField(
        max_length=10, choices=ContentType.choices, default=ContentType.AUDIO
    )
    drive_file_id = models.CharField(
        max_length=255, help_text="Google Drive file ID"
    )
    drive_url = models.URLField(
        max_length=500, blank=True,
        help_text="Direct Google Drive URL (auto-generated from file ID if blank)",
    )
    file_hash = models.CharField(
        max_length=128, blank=True,
        help_text="MD5 hash of the file for change detection",
    )
    last_modified_remote = models.DateTimeField(
        null=True, blank=True,
        help_text="Last modified timestamp from Google Drive",
    )
    duration_seconds = models.PositiveIntegerField(
        null=True, blank=True, help_text="Duration in seconds (audio only)"
    )
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    search_fields = [
        index.SearchField("title"),
        index.SearchField("description"),
        index.RelatedFields("author", [index.SearchField("name")]),
        index.RelatedFields("subject", [index.SearchField("name")]),
    ]

    panels = [
        FieldPanel("title"),
        FieldPanel("author"),
        FieldPanel("subject"),
        FieldPanel("year"),
        FieldPanel("tags"),
        FieldPanel("content_type"),
        FieldPanel("drive_file_id"),
        FieldPanel("drive_url"),
        FieldPanel("file_hash"),
        FieldPanel("last_modified_remote"),
        FieldPanel("duration_seconds"),
        FieldPanel("file_size_bytes"),
        FieldPanel("description"),
    ]

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.drive_file_id and not self.drive_url:
            self.drive_url = (
                f"https://drive.google.com/uc?export=download&id={self.drive_file_id}"
            )
        super().save(*args, **kwargs)
