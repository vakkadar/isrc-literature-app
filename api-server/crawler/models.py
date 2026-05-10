import hashlib
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from django.db import models
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet

from content.models import Language, Person


class LineageGroup(models.TextChoices):
    A_BABUJI = "A_BABUJI", "A — Babuji + direct disciples"
    B_LALAJI_DIRECT = "B_LALAJI_DIRECT", "B — Lalaji's direct disciples"
    C_LINEAGE = "C_LINEAGE", "C — Lalaji's predecessor lineage"


def normalize_url(url: str) -> str:
    if not url:
        return ""
    p = urlparse(url.strip())
    scheme = (p.scheme or "https").lower()
    netloc = p.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = p.path.rstrip("/") or "/"
    drop = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid", "ref", "ref_src"}
    qs = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k.lower() not in drop]
    qs.sort()
    return urlunparse((scheme, netloc, path, "", urlencode(qs), ""))


def url_hash(url: str) -> str:
    return hashlib.sha256(normalize_url(url).encode("utf-8")).hexdigest()


@register_snippet
class PersonAlias(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="aliases")
    alias = models.CharField(max_length=255)
    language = models.CharField(max_length=20, blank=True, help_text="ISO code or freeform (en, hi, ta, ...)")
    is_primary = models.BooleanField(default=False)

    panels = [
        FieldPanel("person"),
        FieldPanel("alias"),
        FieldPanel("language"),
        FieldPanel("is_primary"),
    ]

    class Meta:
        ordering = ["person", "alias"]
        unique_together = [("person", "alias")]
        verbose_name_plural = "person aliases"

    def __str__(self):
        return f"{self.person.name} — {self.alias}"


@register_snippet
class DisambiguationKeyword(models.Model):
    class Weight(models.TextChoices):
        HARD = "hard", "Hard (strong include)"
        SOFT = "soft", "Soft (supportive)"
        UNCERTAIN = "uncertain", "Uncertain (verify)"

    term = models.CharField(max_length=255, unique=True)
    weight = models.CharField(max_length=10, choices=Weight.choices, default=Weight.SOFT)
    applies_to_groups = models.JSONField(default=list, help_text="List of LineageGroup codes; empty = all groups")
    enabled = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    panels = [
        FieldPanel("term"),
        FieldPanel("weight"),
        FieldPanel("applies_to_groups"),
        FieldPanel("enabled"),
        FieldPanel("notes"),
    ]

    class Meta:
        ordering = ["weight", "term"]

    def __str__(self):
        return f"[{self.weight}] {self.term}"


@register_snippet
class Source(models.Model):
    class Type(models.TextChoices):
        WEB = "web", "Web search"
        ARCHIVE = "archive", "Internet Archive"
        YOUTUBE = "youtube", "YouTube"
        GOOGLE_BOOKS = "google_books", "Google Books"
        OPEN_LIBRARY = "open_library", "OpenLibrary"
        PODCAST = "podcast", "Podcast directory"
        OFFICIAL_SITE = "official_site", "Official site"

    code = models.SlugField(max_length=50, unique=True, help_text="Stable identifier used by source modules")
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=Type.choices)
    enabled = models.BooleanField(default=True)
    applies_to_groups = models.JSONField(default=list, help_text="List of LineageGroup codes; empty = all groups")
    max_per_term = models.PositiveIntegerField(default=10)
    rate_limit_seconds = models.FloatField(default=2.0)
    config = models.JSONField(default=dict, blank=True, help_text="Source-specific config (URLs, params)")
    notes = models.TextField(blank=True)

    panels = [
        FieldPanel("code"),
        FieldPanel("name"),
        FieldPanel("type"),
        FieldPanel("enabled"),
        FieldPanel("applies_to_groups"),
        FieldPanel("max_per_term"),
        FieldPanel("rate_limit_seconds"),
        FieldPanel("config"),
        FieldPanel("notes"),
    ]

    class Meta:
        ordering = ["type", "name"]

    def __str__(self):
        return f"{self.name} ({self.type})"


class CrawlRun(models.Model):
    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        PARTIAL = "partial", "Partial (some sources failed)"
        FAILED = "failed", "Failed"

    group = models.CharField(max_length=20, choices=LineageGroup.choices)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.RUNNING)
    triggered_by = models.CharField(max_length=50, default="manual", help_text="cron | manual | <user>")
    stats = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [models.Index(fields=["group", "-started_at"])]

    def __str__(self):
        return f"{self.group} @ {self.started_at:%Y-%m-%d %H:%M}"


class ContentTypeChoice(models.TextChoices):
    AUDIO = "audio", "Audio"
    VIDEO = "video", "Video"
    BOOK = "book", "Book"
    ARTICLE = "article", "Article"
    PDF = "pdf", "PDF"
    IMAGE = "image", "Image"
    OTHER = "other", "Other"


@register_snippet
class Discovery(models.Model):
    """A single hit returned by a source, dedup'd, scored, and persisted."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        REVIEWED = "reviewed", "Reviewed"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    run = models.ForeignKey(CrawlRun, on_delete=models.CASCADE, related_name="discoveries")
    person = models.ForeignKey(
        Person, on_delete=models.SET_NULL, null=True, blank=True, related_name="crawler_discoveries"
    )
    group = models.CharField(max_length=20, choices=LineageGroup.choices)
    url = models.URLField(max_length=2000)
    url_hash = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=500)
    snippet = models.TextField(blank=True)
    source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name="discoveries")
    content_type = models.CharField(max_length=20, choices=ContentTypeChoice.choices, default=ContentTypeChoice.ARTICLE)
    language = models.ForeignKey(
        Language, on_delete=models.SET_NULL, null=True, blank=True, related_name="crawler_discoveries"
    )
    publish_date = models.DateField(null=True, blank=True)
    score = models.FloatField(default=0.0)
    matched_aliases = models.JSONField(default=list, blank=True)
    matched_keywords = models.JSONField(default=list, blank=True)
    dimensions = models.JSONField(default=dict, blank=True, help_text="Extra categorization tags")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW)
    discovered_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("url"),
        FieldPanel("source"),
        FieldPanel("content_type"),
        FieldPanel("snippet"),
        FieldPanel("person"),
        FieldPanel("group"),
        FieldPanel("language"),
        FieldPanel("publish_date"),
        FieldPanel("score"),
        FieldPanel("status"),
    ]

    class Meta:
        ordering = ["-discovered_at"]
        verbose_name_plural = "discoveries"
        indexes = [
            models.Index(fields=["run", "person"]),
            models.Index(fields=["group", "-discovered_at"]),
            models.Index(fields=["publish_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.title[:80]

    def save(self, *args, **kwargs):
        if not self.url_hash and self.url:
            self.url_hash = url_hash(self.url)
        super().save(*args, **kwargs)


@register_snippet
class CandidatePerson(models.Model):
    """A name surfaced from crawl results that may belong to a lineage group; awaits approval."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    name = models.CharField(max_length=255)
    suggested_group = models.CharField(max_length=20, choices=LineageGroup.choices, blank=True)
    evidence_url = models.URLField(max_length=2000, blank=True)
    evidence_text = models.TextField(blank=True)
    occurrence_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_person = models.ForeignKey(
        Person, on_delete=models.SET_NULL, null=True, blank=True, related_name="from_candidates"
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("suggested_group"),
        FieldPanel("evidence_url"),
        FieldPanel("evidence_text"),
        FieldPanel("occurrence_count"),
        FieldPanel("status"),
    ]

    class Meta:
        ordering = ["-occurrence_count", "name"]
        unique_together = [("name", "suggested_group")]

    def __str__(self):
        return f"{self.name} ({self.status})"
