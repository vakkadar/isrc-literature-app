from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel
from wagtail.search import index


@register_snippet
class Person(index.Indexed, models.Model):
    class Role(models.TextChoices):
        MASTER = "master", "Master"
        DISCIPLE = "disciple", "Disciple"
        RESEARCHER = "researcher", "Researcher"
        OTHER = "other", "Other"

    name = models.CharField(max_length=255, unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MASTER)
    description = models.TextField(blank=True)

    search_fields = [
        index.SearchField("name"),
    ]

    panels = [
        FieldPanel("name"),
        FieldPanel("role"),
        FieldPanel("description"),
    ]

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "people"

    def __str__(self):
        return self.name


@register_snippet
class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("code"),
    ]

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


@register_snippet
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("icon"),
    ]

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

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
class Collection(index.Indexed, models.Model):
    title = models.CharField(max_length=500)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="collections")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="collections"
    )
    language = models.ForeignKey(
        Language, on_delete=models.SET_NULL, null=True, blank=True, related_name="collections"
    )
    description = models.TextField(blank=True)
    year = models.IntegerField(null=True, blank=True)

    search_fields = [
        index.SearchField("title"),
        index.SearchField("description"),
    ]

    panels = [
        FieldPanel("title"),
        FieldPanel("person"),
        FieldPanel("category"),
        FieldPanel("language"),
        FieldPanel("description"),
        FieldPanel("year"),
    ]

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


@register_snippet
class ContentItem(index.Indexed, models.Model):
    class ContentType(models.TextChoices):
        PDF = "pdf", "PDF"
        AUDIO = "audio", "Audio"
        VIDEO = "video", "Video"
        IMAGE = "image", "Image"
        LINK = "link", "Link"

    title = models.CharField(max_length=500)
    collection = models.ForeignKey(
        Collection, on_delete=models.SET_NULL, null=True, blank=True, related_name="items"
    )
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="content_items")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="content_items"
    )
    language = models.ForeignKey(
        Language, on_delete=models.SET_NULL, null=True, blank=True, related_name="content_items"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="content_items")
    content_type = models.CharField(max_length=10, choices=ContentType.choices)
    file = models.FileField(upload_to="content/", blank=True)
    source_url = models.URLField(max_length=1000, blank=True)
    external_url = models.URLField(max_length=1000, blank=True)
    description = models.TextField(blank=True)
    year = models.IntegerField(null=True, blank=True)
    chapter_number = models.IntegerField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    search_fields = [
        index.SearchField("title"),
        index.SearchField("description"),
        index.RelatedFields("person", [index.SearchField("name")]),
    ]

    panels = [
        FieldPanel("title"),
        FieldPanel("collection"),
        FieldPanel("person"),
        FieldPanel("category"),
        FieldPanel("language"),
        FieldPanel("tags"),
        FieldPanel("content_type"),
        FieldPanel("file"),
        FieldPanel("source_url"),
        FieldPanel("external_url"),
        FieldPanel("description"),
        FieldPanel("year"),
        FieldPanel("chapter_number"),
        FieldPanel("duration_seconds"),
        FieldPanel("file_size_bytes"),
    ]

    class Meta:
        ordering = ["collection", "chapter_number", "-created_at"]

    def __str__(self):
        return self.title


@register_snippet
class Discovery(models.Model):
    class Source(models.TextChoices):
        GOOGLE = "google", "Google"
        DUCKDUCKGO = "duckduckgo", "DuckDuckGo"
        YOUTUBE = "youtube", "YouTube"
        ARCHIVE = "archive", "Archive"
        OTHER = "other", "Other"

    class DiscoveryContentType(models.TextChoices):
        PDF = "pdf", "PDF"
        AUDIO = "audio", "Audio"
        VIDEO = "video", "Video"
        IMAGE = "image", "Image"
        ARTICLE = "article", "Article"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    title = models.CharField(max_length=500)
    url = models.URLField(max_length=1000)
    source = models.CharField(max_length=50, choices=Source.choices)
    content_type = models.CharField(max_length=10, choices=DiscoveryContentType.choices)
    snippet = models.TextField(blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    person_mentioned = models.ForeignKey(
        Person, on_delete=models.SET_NULL, null=True, blank=True, related_name="discoveries"
    )
    search_term_used = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    discovered_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("url"),
        FieldPanel("source"),
        FieldPanel("content_type"),
        FieldPanel("snippet"),
        FieldPanel("thumbnail_url"),
        FieldPanel("person_mentioned"),
        FieldPanel("search_term_used"),
        FieldPanel("status"),
        FieldPanel("reviewed_at"),
    ]

    class Meta:
        ordering = ["-discovered_at"]
        verbose_name_plural = "discoveries"

    def __str__(self):
        return self.title


@register_snippet
class CrawlerSearchTerm(models.Model):
    term = models.CharField(max_length=500)
    person = models.ForeignKey(
        Person, on_delete=models.SET_NULL, null=True, blank=True, related_name="search_terms"
    )
    enabled = models.BooleanField(default=True)
    last_searched = models.DateTimeField(null=True, blank=True)

    panels = [
        FieldPanel("term"),
        FieldPanel("person"),
        FieldPanel("enabled"),
        FieldPanel("last_searched"),
    ]

    class Meta:
        ordering = ["term"]

    def __str__(self):
        return self.term
