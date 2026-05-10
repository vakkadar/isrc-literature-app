from __future__ import annotations

import re
from typing import Iterable, Optional

from crawler.sources import RawHit

from .base import BaseFilter, FilterResult


HARD_WEIGHT = 3.0
SOFT_WEIGHT = 1.0
UNCERTAIN_WEIGHT = 0.0

INCLUDE_SCORE_THRESHOLD = 2.0
UNCERTAIN_MIN_SCORE = 0.0


def _normalize(text: str) -> str:
    return (text or "").lower()


def _word_boundary_pattern(term: str) -> re.Pattern[str]:
    t = re.escape(term.strip().lower())
    return re.compile(rf"(?<![\w]){t}(?![\w])", re.IGNORECASE)


class RuleBasedFilter(BaseFilter):
    """Rule-based: requires an alias match, scores hard/soft keywords, surfaces uncertain."""

    def __init__(self, keywords: Iterable):
        self._kw_cache: list[tuple[str, str, list[str], re.Pattern[str]]] = []
        for kw in keywords:
            if not kw.enabled:
                continue
            self._kw_cache.append(
                (kw.term, kw.weight, list(kw.applies_to_groups or []), _word_boundary_pattern(kw.term))
            )

    def _alias_strings(self, person) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for n in [getattr(person, "name", None), *(a.alias for a in person.aliases.all())]:
            if not n:
                continue
            key = n.strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(n.strip())
        return out

    def evaluate(self, hit: RawHit, person, group: str) -> FilterResult:
        text = " ".join([hit.title or "", hit.snippet or ""])
        text_lower = _normalize(text)

        matched_aliases: list[str] = []
        for alias in self._alias_strings(person):
            if _word_boundary_pattern(alias).search(text_lower):
                matched_aliases.append(alias)

        if not matched_aliases:
            return FilterResult(score=0.0, decision="reject", reason="no alias match")

        score = 0.0
        matched_keywords: list[str] = []
        uncertain_seen = False

        for term, weight, applies_to, pat in self._kw_cache:
            if applies_to and group not in applies_to:
                continue
            if pat.search(text_lower):
                matched_keywords.append(f"{weight}:{term}")
                if weight == "hard":
                    score += HARD_WEIGHT
                elif weight == "soft":
                    score += SOFT_WEIGHT
                elif weight == "uncertain":
                    uncertain_seen = True

        score += len(matched_aliases) * 1.5

        if uncertain_seen and score < INCLUDE_SCORE_THRESHOLD + HARD_WEIGHT:
            decision = "uncertain"
            reason = "uncertain keyword present"
        elif score >= INCLUDE_SCORE_THRESHOLD:
            decision = "include"
            reason = "alias + score threshold"
        elif score >= UNCERTAIN_MIN_SCORE:
            decision = "uncertain"
            reason = "below threshold but alias matched"
        else:
            decision = "reject"
            reason = "score too low"

        return FilterResult(
            score=round(score, 3),
            decision=decision,
            matched_aliases=matched_aliases,
            matched_keywords=matched_keywords,
            reason=reason,
        )
