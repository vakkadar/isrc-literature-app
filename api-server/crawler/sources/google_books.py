from __future__ import annotations

import os
from datetime import date, datetime
from typing import Iterable, Optional

import requests

from .base import BaseSource, RawHit, logger


class GoogleBooksSource(BaseSource):
    """Google Books volumes.list — key optional but recommended for higher quota."""

    code = "google_books"
    type = "google_books"

    BASE = "https://www.googleapis.com/books/v1/volumes"

    def search(self, query: str, max_results: int, since: Optional[date] = None) -> Iterable[RawHit]:
        self._throttle()
        params = {
            "q": query,
            "maxResults": min(max_results, 40),
            "printType": "books",
        }
        key = self.config.get("api_key") or os.environ.get("GOOGLE_BOOKS_API_KEY", "")
        if key:
            params["key"] = key

        try:
            resp = requests.get(self.BASE, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning("Google Books search failed for %r: %s", query, e)
            return

        for item in data.get("items", []):
            vinfo = item.get("volumeInfo", {})
            title = vinfo.get("title")
            url = vinfo.get("infoLink") or vinfo.get("canonicalVolumeLink")
            if not title or not url:
                continue
            pub_date = None
            pub = vinfo.get("publishedDate", "")
            if pub:
                for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
                    try:
                        pub_date = datetime.strptime(pub, fmt).date()
                        break
                    except ValueError:
                        continue
            if since and pub_date and pub_date < since:
                continue
            authors = vinfo.get("authors") or []
            snippet_parts = []
            if authors:
                snippet_parts.append("By " + ", ".join(authors))
            if vinfo.get("description"):
                snippet_parts.append(vinfo["description"][:800])
            yield RawHit(
                url=url,
                title=title,
                snippet="\n".join(snippet_parts),
                content_type="book",
                language=(vinfo.get("language") or "")[:20],
                publish_date=pub_date,
                raw=item,
            )
