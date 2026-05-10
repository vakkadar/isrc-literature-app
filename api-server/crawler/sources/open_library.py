from __future__ import annotations

from datetime import date, datetime
from typing import Iterable, Optional

import requests

from .base import BaseSource, RawHit, logger


class OpenLibrarySource(BaseSource):
    code = "open_library"
    type = "open_library"

    BASE = "https://openlibrary.org/search.json"

    def search(self, query: str, max_results: int, since: Optional[date] = None) -> Iterable[RawHit]:
        self._throttle()
        params = {
            "q": query,
            "limit": min(max_results, 100),
            "fields": "key,title,author_name,first_publish_year,language,subject",
        }
        try:
            resp = requests.get(self.BASE, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning("OpenLibrary search failed for %r: %s", query, e)
            return

        for doc in data.get("docs", []):
            key = doc.get("key")
            title = doc.get("title")
            if not key or not title:
                continue
            year = doc.get("first_publish_year")
            pub_date = None
            if year:
                try:
                    pub_date = datetime(int(year), 1, 1).date()
                except (TypeError, ValueError):
                    pub_date = None
            if since and pub_date and pub_date < since:
                continue
            authors = doc.get("author_name") or []
            languages = doc.get("language") or []
            lang = languages[0] if languages else ""
            yield RawHit(
                url=f"https://openlibrary.org{key}",
                title=title,
                snippet=("By " + ", ".join(authors)) if authors else "",
                content_type="book",
                language=lang[:20],
                publish_date=pub_date,
                raw=doc,
            )
