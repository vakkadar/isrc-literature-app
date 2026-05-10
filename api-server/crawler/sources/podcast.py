from __future__ import annotations

import os
from datetime import date, datetime, timezone
from typing import Iterable, Optional

import requests

from .base import BaseSource, RawHit, SourceConfigError, logger


class ListenNotesSource(BaseSource):
    """Listen Notes search API — requires LISTENNOTES_API_KEY (free tier 300/mo)."""

    code = "listen_notes"
    type = "podcast"

    BASE = "https://listen-api.listennotes.com/api/v2/search"

    def _key(self) -> str:
        key = self.config.get("api_key") or os.environ.get("LISTENNOTES_API_KEY", "")
        if not key:
            raise SourceConfigError("LISTENNOTES_API_KEY not set; skipping podcast source")
        return key

    def search(self, query: str, max_results: int, since: Optional[date] = None) -> Iterable[RawHit]:
        try:
            key = self._key()
        except SourceConfigError as e:
            logger.info(str(e))
            return

        self._throttle()
        params = {"q": query, "type": "episode", "safe_mode": 0}
        if since:
            params["published_after"] = int(datetime(since.year, since.month, since.day, tzinfo=timezone.utc).timestamp() * 1000)

        try:
            resp = requests.get(self.BASE, params=params, headers={"X-ListenAPI-Key": key}, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning("Listen Notes search failed for %r: %s", query, e)
            return

        for ep in data.get("results", [])[:max_results]:
            url = ep.get("link") or ep.get("audio")
            title = ep.get("title_original") or ep.get("title")
            if not url or not title:
                continue
            pub_date = None
            pub_ms = ep.get("pub_date_ms")
            if pub_ms:
                try:
                    pub_date = datetime.fromtimestamp(int(pub_ms) / 1000, tz=timezone.utc).date()
                except (TypeError, ValueError):
                    pub_date = None
            yield RawHit(
                url=url,
                title=title,
                snippet=(ep.get("description_original") or ep.get("description") or "")[:1000],
                content_type="audio",
                publish_date=pub_date,
                raw=ep,
            )
