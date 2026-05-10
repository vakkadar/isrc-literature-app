from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from crawler.sources import RawHit


@dataclass
class FilterResult:
    score: float
    decision: str  # 'include' | 'uncertain' | 'reject'
    matched_aliases: list[str] = field(default_factory=list)
    matched_keywords: list[str] = field(default_factory=list)
    reason: str = ""


class BaseFilter:
    def evaluate(self, hit: RawHit, person, group: str) -> FilterResult:
        raise NotImplementedError
