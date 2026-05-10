from __future__ import annotations

from datetime import date, datetime
from typing import Iterable, Optional

import requests

from .base import BaseSource, RawHit, logger


MEDIATYPE_TO_CONTENT = {
    "audio": "audio",
    "movies": "video",
    "texts": "book",
    "image": "image",
}


class ArchiveOrgSource(BaseSource):
    """Internet Archive advancedsearch.php — public, no key."""

    code = "archive_org"
    type = "archive"

    BASE = "https://archive.org/advancedsearch.php"

    def search(self, query: str, max_results: int, since: Optional[date] = None) -> Iterable[RawHit]:
        self._throttle()
        q = query
        if since:
            q = f"({q}) AND publicdate:[{since.isoformat()} TO 9999-12-31]"
        params = {
            "q": q,
            "fl[]": ["identifier", "title", "description", "mediatype", "publicdate", "language", "creator"],
            "rows": max_results,
            "page": 1,
            "output": "json",
        }
        try:
            resp = requests.get(self.BASE, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning("archive.org search failed for %r: %s", query, e)
            return

        for doc in data.get("response", {}).get("docs", []):
            identifier = doc.get("identifier")
            title = doc.get("title") or ""
            if not identifier or not title:
                continue
            url = f"https://archive.org/details/{identifier}"
            mediatype = doc.get("mediatype", "")
            ctype = MEDIATYPE_TO_CONTENT.get(mediatype, "other")
            pub = doc.get("publicdate")
            pub_date = None
            if pub:
                try:
                    pub_date = datetime.fromisoformat(pub.replace("Z", "+00:00")).date()
                except Exception:
                    pub_date = None
            lang = doc.get("language") or ""
            if isinstance(lang, list):
                lang = lang[0] if lang else ""
            yield RawHit(
                url=url,
                title=title if isinstance(title, str) else " ".join(title),
                snippet=(doc.get("description") or "")[:1000] if isinstance(doc.get("description"), str) else "",
                content_type=ctype,
                language=lang[:20] if lang else "",
                publish_date=pub_date,
                raw=doc,
            )
