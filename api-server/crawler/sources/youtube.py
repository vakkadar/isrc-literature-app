from __future__ import annotations

import os
from datetime import date, datetime
from typing import Iterable, Optional

import requests

from .base import BaseSource, RawHit, SourceConfigError, logger


class YouTubeSource(BaseSource):
    """YouTube Data API v3 search.list — requires YOUTUBE_API_KEY env var."""

    code = "youtube"
    type = "youtube"

    BASE = "https://www.googleapis.com/youtube/v3/search"

    def _key(self) -> str:
        key = self.config.get("api_key") or os.environ.get("YOUTUBE_API_KEY", "")
        if not key:
            raise SourceConfigError("YOUTUBE_API_KEY not set; skipping YouTube source")
        return key

    def search(self, query: str, max_results: int, since: Optional[date] = None) -> Iterable[RawHit]:
        try:
            key = self._key()
        except SourceConfigError as e:
            logger.info(str(e))
            return

        self._throttle()
        params = {
            "key": key,
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": min(max_results, 50),
            "safeSearch": "none",
        }
        if since:
            params["publishedAfter"] = f"{since.isoformat()}T00:00:00Z"

        try:
            resp = requests.get(self.BASE, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning("YouTube search failed for %r: %s", query, e)
            return

        for item in data.get("items", []):
            vid = item.get("id", {}).get("videoId")
            sn = item.get("snippet", {})
            if not vid or not sn:
                continue
            pub_date = None
            pub = sn.get("publishedAt")
            if pub:
                try:
                    pub_date = datetime.fromisoformat(pub.replace("Z", "+00:00")).date()
                except Exception:
                    pub_date = None
            yield RawHit(
                url=f"https://www.youtube.com/watch?v={vid}",
                title=sn.get("title", ""),
                snippet=sn.get("description", ""),
                content_type="video",
                publish_date=pub_date,
                raw=item,
            )
