from __future__ import annotations

from datetime import date
from typing import Iterable, Optional

from .base import BaseSource, RawHit, SourceError, logger


class WebSource(BaseSource):
    code = "web_ddg"
    type = "web"

    def search(self, query: str, max_results: int, since: Optional[date] = None) -> Iterable[RawHit]:
        try:
            from duckduckgo_search import DDGS
        except ImportError as e:
            raise SourceError(f"duckduckgo_search not installed: {e}") from e

        self._throttle()
        with DDGS() as ddgs:
            try:
                results = list(ddgs.text(query, max_results=max_results, region="wt-wt", safesearch="off"))
            except Exception as e:
                logger.warning("DDG text search failed for %r: %s", query, e)
                return

        for r in results:
            url = r.get("href") or r.get("url") or ""
            title = r.get("title") or ""
            snippet = r.get("body") or r.get("snippet") or ""
            if not url or not title:
                continue
            yield RawHit(
                url=url,
                title=title,
                snippet=snippet,
                content_type="article",
                raw=r,
            )


class OfficialSiteSource(BaseSource):
    """Site-restricted DDG queries against a list of official domains in config['domains']."""

    code = "official_sites"
    type = "official_site"

    def search(self, query: str, max_results: int, since: Optional[date] = None) -> Iterable[RawHit]:
        try:
            from duckduckgo_search import DDGS
        except ImportError as e:
            raise SourceError(f"duckduckgo_search not installed: {e}") from e

        domains = self.config.get("domains") or ["heartfulness.org", "sahajmarg.org"]
        per_domain = max(1, max_results // max(1, len(domains)))

        for domain in domains:
            self._throttle()
            scoped = f"site:{domain} {query}"
            with DDGS() as ddgs:
                try:
                    results = list(ddgs.text(scoped, max_results=per_domain, region="wt-wt", safesearch="off"))
                except Exception as e:
                    logger.warning("DDG site:%s failed for %r: %s", domain, query, e)
                    continue
            for r in results:
                url = r.get("href") or r.get("url") or ""
                title = r.get("title") or ""
                snippet = r.get("body") or r.get("snippet") or ""
                if not url or not title:
                    continue
                yield RawHit(
                    url=url,
                    title=title,
                    snippet=snippet,
                    content_type="article",
                    raw={"domain": domain, **r},
                )
