from __future__ import annotations

import logging
import os
from typing import Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import CrawlRun, Discovery, LineageGroup

logger = logging.getLogger(__name__)


GROUP_LABELS = {
    LineageGroup.A_BABUJI.value: "Group A — Babuji & direct disciples",
    LineageGroup.B_LALAJI_DIRECT.value: "Group B — Lalaji's direct disciples",
    LineageGroup.C_LINEAGE.value: "Group C — Lalaji's predecessor lineage",
}


def _recipients() -> list[str]:
    raw = os.environ.get("CRAWLER_DIGEST_TO", "rajkumar.vakkada@gmail.com")
    return [r.strip() for r in raw.split(",") if r.strip()]


def build_digest_context(run: CrawlRun) -> Optional[dict]:
    """Build a context dict for the digest template, or None if nothing to send."""
    discoveries = (
        Discovery.objects.filter(run=run, status=Discovery.Status.NEW)
        .select_related("person", "source")
        .order_by("-score", "-discovered_at")
    )
    if not discoveries.exists():
        return None

    by_person: dict[str, list[Discovery]] = {}
    for d in discoveries:
        key = d.person.name if d.person else "(unattributed)"
        by_person.setdefault(key, []).append(d)

    return {
        "run": run,
        "group_label": GROUP_LABELS.get(run.group, run.group),
        "total": discoveries.count(),
        "by_person": by_person,
        "stats": run.stats or {},
    }


def send_group_digest(run: CrawlRun) -> bool:
    """Send digest for one CrawlRun. Returns True if an email went out, False if skipped."""
    ctx = build_digest_context(run)
    if ctx is None:
        logger.info("digest skipped for run=%s group=%s (zero discoveries)", run.id, run.group)
        return False

    text_body = render_to_string("crawler/digest.txt", ctx)
    html_body = render_to_string("crawler/digest.html", ctx)
    subject = f"[ISRC crawler] {ctx['group_label']} — {ctx['total']} new"
    recipients = _recipients()

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@isrc-literature.org"),
        to=recipients,
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)
    logger.info("digest sent run=%s group=%s to=%s items=%s", run.id, run.group, recipients, ctx["total"])
    return True
