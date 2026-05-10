from __future__ import annotations

import logging
import traceback
from datetime import date, datetime
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from content.models import Person
from crawler.filter import RuleBasedFilter
from crawler.reports import send_group_digest
from crawler.models import (
    CrawlRun,
    DisambiguationKeyword,
    Discovery,
    LineageGroup,
    Source,
    url_hash,
)
from crawler.sources import RawHit, SourceConfigError, SourceError, get_source


logger = logging.getLogger(__name__)


VALID_GROUPS = [c for c, _ in LineageGroup.choices]


class Command(BaseCommand):
    help = "Run the multi-source crawler for one or all lineage groups."

    def add_arguments(self, parser):
        parser.add_argument(
            "--group",
            required=True,
            choices=VALID_GROUPS + ["all"],
            help="Lineage group code or 'all'",
        )
        parser.add_argument("--person", help="Restrict to a single Person.name match")
        parser.add_argument("--since", help="YYYY-MM-DD lower bound for source date filters")
        parser.add_argument("--max-per-source", type=int, help="Override Source.max_per_term")
        parser.add_argument("--dry-run", action="store_true", help="Run sources + filter but don't write Discoveries")
        parser.add_argument("--no-digest", action="store_true", help="Skip sending digest email after the run")
        parser.add_argument("--triggered-by", default="manual", help="Marker for CrawlRun.triggered_by")

    def handle(self, *args, **opts):
        groups = VALID_GROUPS if opts["group"] == "all" else [opts["group"]]
        since = self._parse_since(opts.get("since"))
        for group in groups:
            try:
                self._run_group(
                    group=group,
                    person_name=opts.get("person"),
                    since=since,
                    max_per_source=opts.get("max_per_source"),
                    dry_run=opts.get("dry_run", False),
                    no_digest=opts.get("no_digest", False),
                    triggered_by=opts.get("triggered_by") or "manual",
                )
            except Exception as e:
                logger.exception("crawler run for group %s crashed", group)
                self.stderr.write(self.style.ERROR(f"[{group}] crashed: {e}"))

    def _parse_since(self, raw: Optional[str]) -> Optional[date]:
        if not raw:
            return None
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError as e:
            raise CommandError(f"--since must be YYYY-MM-DD: {e}")

    def _last_success(self, group: str) -> Optional[date]:
        last = (
            CrawlRun.objects.filter(group=group, status__in=[CrawlRun.Status.SUCCESS, CrawlRun.Status.PARTIAL])
            .order_by("-started_at")
            .values_list("started_at", flat=True)
            .first()
        )
        return last.date() if last else None

    def _run_group(
        self,
        *,
        group: str,
        person_name: Optional[str],
        since: Optional[date],
        max_per_source: Optional[int],
        dry_run: bool,
        no_digest: bool,
        triggered_by: str,
    ):
        effective_since = since or self._last_success(group)

        persons = Person.objects.filter(lineage_group=group, crawl_active=True)
        if person_name:
            persons = persons.filter(name__iexact=person_name)
        persons = list(persons)

        if not persons:
            self.stdout.write(self.style.WARNING(f"[{group}] no active persons; skipping"))
            return

        sources = list(Source.objects.filter(enabled=True))
        sources = [s for s in sources if not s.applies_to_groups or group in s.applies_to_groups]
        if not sources:
            self.stdout.write(self.style.WARNING(f"[{group}] no enabled sources for this group; skipping"))
            return

        keywords = list(DisambiguationKeyword.objects.all())
        flt = RuleBasedFilter(keywords)

        run = CrawlRun.objects.create(
            group=group,
            status=CrawlRun.Status.RUNNING,
            triggered_by=triggered_by,
            stats={"since": effective_since.isoformat() if effective_since else None, "dry_run": dry_run},
        )
        self.stdout.write(
            f"[{group}] run #{run.id} start: {len(persons)} persons x {len(sources)} sources "
            f"since={effective_since} dry_run={dry_run}"
        )

        per_source_stats: dict[str, dict[str, int]] = {}
        any_error = False
        any_ok = False

        try:
            for src_model in sources:
                stats = per_source_stats.setdefault(
                    src_model.code,
                    {"queries": 0, "raw_hits": 0, "deduped": 0, "kept_new": 0, "uncertain": 0, "rejected": 0, "errors": 0},
                )
                try:
                    source = get_source(src_model)
                except SourceError as e:
                    self.stderr.write(self.style.WARNING(f"[{group}] {src_model.code}: {e}"))
                    stats["errors"] += 1
                    any_error = True
                    continue

                cap = max_per_source if max_per_source is not None else src_model.max_per_term

                for person in persons:
                    if group == LineageGroup.C_LINEAGE.value:
                        aliases = [
                            a for a in person.aliases.all() if not a.language or a.language.lower() in {"en", "english"}
                        ]
                    else:
                        aliases = list(person.aliases.all())

                    query = person.name
                    primary = next((a for a in aliases if a.is_primary), None)
                    if primary:
                        query = f"{primary.alias} {person.name}".strip()

                    stats["queries"] += 1
                    try:
                        hits = list(source.search(query=query, max_results=cap, since=effective_since))
                    except SourceConfigError as e:
                        self.stdout.write(f"[{group}] {src_model.code}: {e}")
                        stats["errors"] += 1
                        break
                    except Exception as e:
                        logger.exception("source %s search failed", src_model.code)
                        self.stderr.write(self.style.ERROR(f"[{group}] {src_model.code}: {e}"))
                        stats["errors"] += 1
                        any_error = True
                        continue

                    stats["raw_hits"] += len(hits)
                    self._process_hits(
                        run=run,
                        group=group,
                        person=person,
                        source_model=src_model,
                        hits=hits,
                        flt=flt,
                        dry_run=dry_run,
                        stats=stats,
                    )
                    any_ok = True

        finally:
            stats_summary = {
                "since": effective_since.isoformat() if effective_since else None,
                "dry_run": dry_run,
                "per_source": per_source_stats,
            }
            run.finished_at = timezone.now()
            if any_ok and not any_error:
                run.status = CrawlRun.Status.SUCCESS
            elif any_ok and any_error:
                run.status = CrawlRun.Status.PARTIAL
            else:
                run.status = CrawlRun.Status.FAILED
                run.error = run.error or "no successful sources"
            run.stats = stats_summary
            run.save(update_fields=["finished_at", "status", "stats", "error"])
            self.stdout.write(self.style.SUCCESS(f"[{group}] run #{run.id} {run.status}: {per_source_stats}"))

            if not dry_run and not no_digest:
                try:
                    sent = send_group_digest(run)
                    if sent:
                        self.stdout.write(f"[{group}] digest sent")
                    else:
                        self.stdout.write(f"[{group}] digest skipped (zero discoveries)")
                except Exception as e:
                    logger.exception("digest send failed for run=%s", run.id)
                    self.stderr.write(self.style.WARNING(f"[{group}] digest send failed: {e}"))

    def _process_hits(
        self,
        *,
        run,
        group: str,
        person,
        source_model,
        hits: list[RawHit],
        flt: RuleBasedFilter,
        dry_run: bool,
        stats: dict,
    ):
        for hit in hits:
            h_hash = url_hash(hit.url)
            if Discovery.objects.filter(url_hash=h_hash).exists():
                stats["deduped"] += 1
                continue

            result = flt.evaluate(hit, person, group)
            if result.decision == "reject":
                stats["rejected"] += 1
                continue

            if result.decision == "uncertain":
                stats["uncertain"] += 1
            else:
                stats["kept_new"] += 1

            if dry_run:
                continue

            try:
                with transaction.atomic():
                    Discovery.objects.create(
                        run=run,
                        person=person,
                        group=group,
                        url=hit.url,
                        url_hash=h_hash,
                        title=hit.title[:500],
                        snippet=hit.snippet or "",
                        source=source_model,
                        content_type=hit.content_type or "article",
                        publish_date=hit.publish_date,
                        score=result.score,
                        matched_aliases=result.matched_aliases,
                        matched_keywords=result.matched_keywords,
                        dimensions={"reason": result.reason, "raw_lang": hit.language},
                        status=Discovery.Status.NEW,
                    )
            except Exception:
                logger.exception("failed to persist Discovery url=%s", hit.url)
                stats["errors"] = stats.get("errors", 0) + 1
