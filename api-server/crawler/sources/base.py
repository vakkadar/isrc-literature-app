from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import date
from typing import Iterable, Optional

logger = logging.getLogger(__name__)


@dataclass
class RawHit:
    url: str
    title: str
    snippet: str = ""
    content_type: str = "article"
    language: str = ""
    publish_date: Optional[date] = None
    raw: dict = field(default_factory=dict)


class SourceError(Exception):
    pass


class SourceConfigError(SourceError):
    """Raised when a required key/config is missing — should mark source skipped, not fail run."""


class BaseSource:
    """Subclasses set `code` and `type`, implement `search`."""

    code: str = ""
    type: str = ""

    def __init__(self, source_model):
        self.model = source_model
        self.config = source_model.config or {}
        self.rate_limit = float(source_model.rate_limit_seconds or 0)
        self._last_call = 0.0

    def _throttle(self):
        if self.rate_limit <= 0:
            return
        elapsed = time.monotonic() - self._last_call
        wait = self.rate_limit - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def search(self, query: str, max_results: int, since: Optional[date] = None) -> Iterable[RawHit]:
        raise NotImplementedError
