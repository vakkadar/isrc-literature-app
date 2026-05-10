from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .models import (
    CandidatePerson,
    CrawlRun,
    DisambiguationKeyword,
    Discovery,
    PersonAlias,
    Source,
)


class DiscoveryViewSet(SnippetViewSet):
    model = Discovery
    icon = "search"
    menu_label = "Discoveries"
    list_display = ["title", "person", "group", "source", "score", "status", "discovered_at"]
    list_filter = ["group", "status", "source", "content_type"]
    search_fields = ["title", "snippet", "url"]
    ordering = ["-discovered_at"]
    list_per_page = 50


class CandidatePersonViewSet(SnippetViewSet):
    model = CandidatePerson
    icon = "user"
    menu_label = "Candidate persons"
    list_display = ["name", "suggested_group", "occurrence_count", "status", "created_at"]
    list_filter = ["status", "suggested_group"]
    search_fields = ["name", "evidence_text"]
    ordering = ["-occurrence_count", "name"]


class CrawlRunViewSet(SnippetViewSet):
    model = CrawlRun
    icon = "history"
    menu_label = "Crawl runs"
    list_display = ["group", "status", "triggered_by", "started_at", "finished_at"]
    list_filter = ["group", "status"]
    ordering = ["-started_at"]


class SourceViewSet(SnippetViewSet):
    model = Source
    icon = "link"
    menu_label = "Sources"
    list_display = ["code", "name", "type", "enabled", "max_per_term"]
    list_filter = ["type", "enabled"]
    search_fields = ["code", "name"]
    ordering = ["type", "name"]


class DisambiguationKeywordViewSet(SnippetViewSet):
    model = DisambiguationKeyword
    icon = "tag"
    menu_label = "Keywords"
    list_display = ["term", "weight", "enabled"]
    list_filter = ["weight", "enabled"]
    search_fields = ["term", "notes"]
    ordering = ["weight", "term"]


class PersonAliasViewSet(SnippetViewSet):
    model = PersonAlias
    icon = "user"
    menu_label = "Person aliases"
    list_display = ["person", "alias", "language", "is_primary"]
    list_filter = ["language", "is_primary"]
    search_fields = ["alias", "person__name"]
    ordering = ["person", "alias"]


class CrawlerViewSetGroup(SnippetViewSetGroup):
    menu_label = "Crawler"
    menu_icon = "spinner"
    menu_order = 250
    items = (
        DiscoveryViewSet,
        CandidatePersonViewSet,
        CrawlRunViewSet,
        SourceViewSet,
        DisambiguationKeywordViewSet,
        PersonAliasViewSet,
    )


register_snippet(CrawlerViewSetGroup)
