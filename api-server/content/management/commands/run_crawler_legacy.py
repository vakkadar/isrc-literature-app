import logging
import time
import urllib.parse
from datetime import datetime

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from content.models import ContentItem, CrawlerSearchTerm, Discovery

logger = logging.getLogger(__name__)

MAX_PER_SOURCE = 5
SEARCH_DELAY = 2


def guess_content_type(url, title=""):
    url_lower = url.lower()
    title_lower = title.lower()
    if any(ext in url_lower for ext in [".pdf"]):
        return Discovery.DiscoveryContentType.PDF
    if any(ext in url_lower for ext in [".mp3", ".wav", ".flac", ".ogg", ".m4a"]):
        return Discovery.DiscoveryContentType.AUDIO
    if any(d in url_lower for d in ["youtube.com", "youtu.be", "vimeo.com"]) or any(
        ext in url_lower for ext in [".mp4", ".mkv", ".webm"]
    ):
        return Discovery.DiscoveryContentType.VIDEO
    if any(ext in url_lower for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
        return Discovery.DiscoveryContentType.IMAGE
    if "audio" in title_lower or "recording" in title_lower:
        return Discovery.DiscoveryContentType.AUDIO
    if "video" in title_lower:
        return Discovery.DiscoveryContentType.VIDEO
    return Discovery.DiscoveryContentType.ARTICLE


def url_already_known(url):
    return (
        Discovery.objects.filter(url=url).exists()
        or ContentItem.objects.filter(source_url=url).exists()
    )


def search_duckduckgo(term, max_results=10):
    results = []
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            for r in ddgs.text(term, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                    "source": Discovery.Source.DUCKDUCKGO,
                })
    except Exception:
        logger.exception("DuckDuckGo search failed for: %s", term)
    return results


def search_internet_archive(term, max_results=10):
    results = []
    try:
        params = {
            "q": term,
            "output": "json",
            "rows": str(max_results),
            "fl[]": ["identifier", "title", "description", "mediatype"],
        }
        resp = requests.get(
            "https://archive.org/advancedsearch.php",
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        for doc in data.get("response", {}).get("docs", []):
            identifier = doc.get("identifier", "")
            url = f"https://archive.org/details/{identifier}"
            desc = doc.get("description", "")
            if isinstance(desc, list):
                desc = " ".join(desc)
            results.append({
                "title": doc.get("title", identifier),
                "url": url,
                "snippet": (desc[:500] if desc else ""),
                "source": Discovery.Source.ARCHIVE,
            })
    except Exception:
        logger.exception("Internet Archive search failed for: %s", term)
    return results


def search_youtube_rss(term, max_results=10):
    results = []
    try:
        encoded = urllib.parse.quote_plus(term)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        resp = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ISRCLiteratureBot/1.0)"},
        )
        resp.raise_for_status()
        import re

        video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', resp.text)
        seen = set()
        for vid in video_ids:
            if vid in seen:
                continue
            seen.add(vid)
            if len(seen) > max_results:
                break
            results.append({
                "title": f"YouTube video: {vid}",
                "url": f"https://www.youtube.com/watch?v={vid}",
                "snippet": f"Found via YouTube search for: {term}",
                "source": Discovery.Source.YOUTUBE,
            })
    except Exception:
        logger.exception("YouTube search failed for: %s", term)
    return results


class Command(BaseCommand):
    help = "Crawl the web for new content about disciples and masters"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true", help="Print results without saving"
        )
        parser.add_argument(
            "--no-email", action="store_true", help="Skip sending the digest email"
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        no_email = options["no_email"]
        start = timezone.now()

        self.stdout.write(f"[{start:%Y-%m-%d %H:%M}] Starting discovery crawler...")

        terms = CrawlerSearchTerm.objects.filter(enabled=True)
        if not terms.exists():
            self.stdout.write(self.style.WARNING("No enabled search terms found."))
            return

        self.stdout.write(f"Found {terms.count()} enabled search terms.")

        new_discoveries = []
        search_fns = [
            ("DuckDuckGo", search_duckduckgo),
            ("Internet Archive", search_internet_archive),
            ("YouTube", search_youtube_rss),
        ]

        for search_term in terms:
            self.stdout.write(f"\n--- Searching: \"{search_term.term}\" ---")

            for source_name, search_fn in search_fns:
                self.stdout.write(f"  [{source_name}] ", ending="")
                try:
                    results = search_fn(search_term.term, max_results=MAX_PER_SOURCE)
                    saved = 0
                    for r in results:
                        if not r["url"] or url_already_known(r["url"]):
                            continue

                        content_type = guess_content_type(r["url"], r["title"])

                        if dry_run:
                            self.stdout.write(f"    [DRY] {r['title'][:80]} — {r['url']}")
                            saved += 1
                            continue

                        discovery = Discovery.objects.create(
                            title=r["title"][:500],
                            url=r["url"],
                            source=r["source"],
                            content_type=content_type,
                            snippet=r["snippet"][:1000] if r["snippet"] else "",
                            person_mentioned=search_term.person,
                            search_term_used=search_term.term,
                            status=Discovery.Status.PENDING,
                        )
                        new_discoveries.append(discovery)
                        saved += 1

                    self.stdout.write(f"{saved} new / {len(results)} total")
                except Exception:
                    logger.exception("Error in %s for '%s'", source_name, search_term.term)
                    self.stdout.write(self.style.ERROR("error (see logs)"))

                time.sleep(SEARCH_DELAY)

            search_term.last_searched = timezone.now()
            search_term.save(update_fields=["last_searched"])

        elapsed = (timezone.now() - start).total_seconds()
        self.stdout.write(f"\nCrawl finished in {elapsed:.0f}s. {len(new_discoveries)} new discoveries.")

        if new_discoveries and not dry_run and not no_email:
            self.stdout.write("Sending digest email...")
            try:
                send_digest_email(new_discoveries)
                self.stdout.write(self.style.SUCCESS("Digest email sent."))
            except Exception:
                logger.exception("Failed to send digest email")
                self.stdout.write(self.style.ERROR("Failed to send digest email (see logs)."))


def build_digest_html(discoveries):
    by_person = {}
    for d in discoveries:
        key = d.person_mentioned.name if d.person_mentioned else "General / Unlinked"
        by_person.setdefault(key, []).append(d)

    rows = []
    for person_name in sorted(by_person):
        rows.append(f'<h2 style="color:#4a2c0a;border-bottom:1px solid #ccc;padding-bottom:4px;">{person_name}</h2>')
        for d in by_person[person_name]:
            badge_color = {
                "duckduckgo": "#de5833",
                "youtube": "#c4302b",
                "archive": "#428bca",
            }.get(d.source, "#888")
            rows.append(
                f'<div style="margin-bottom:12px;">'
                f'<a href="{d.url}" style="font-size:16px;color:#1a0dab;text-decoration:none;">{d.title}</a><br>'
                f'<span style="background:{badge_color};color:#fff;padding:1px 6px;border-radius:3px;font-size:11px;">'
                f"{d.get_source_display()}</span> "
                f'<span style="background:#6c757d;color:#fff;padding:1px 6px;border-radius:3px;font-size:11px;">'
                f"{d.get_content_type_display()}</span>"
                f'{f"<br><span style=&quot;color:#555;font-size:13px;&quot;>{d.snippet[:200]}</span>" if d.snippet else ""}'
                f"</div>"
            )

    today = datetime.now().strftime("%B %d, %Y")
    return (
        f'<div style="font-family:sans-serif;max-width:700px;margin:auto;padding:20px;">'
        f'<h1 style="color:#4a2c0a;">ISRC Literature — Weekly Discovery Digest</h1>'
        f'<p style="color:#555;">{today} &mdash; <strong>{len(discoveries)}</strong> new item(s) found.</p>'
        f"{''.join(rows)}"
        f'<hr style="margin-top:30px;">'
        f'<p style="color:#888;font-size:12px;">Review and approve these items in the '
        f'<a href="{settings.WAGTAILADMIN_BASE_URL}/admin/snippets/content/discovery/">admin panel</a>.</p>'
        f"</div>"
    )


def send_digest_email(discoveries):
    from django.core.mail import send_mail

    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"ISRC Literature - Weekly Discovery Digest ({today})"
    html_body = build_digest_html(discoveries)
    plain_body = f"{len(discoveries)} new discoveries found. Review them in the admin panel."

    send_mail(
        subject=subject,
        message=plain_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.CRAWLER_DIGEST_EMAIL],
        html_message=html_body,
        fail_silently=False,
    )
