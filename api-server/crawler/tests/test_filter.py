from django.test import SimpleTestCase

from crawler.filter import RuleBasedFilter
from crawler.sources import RawHit


class _Alias:
    def __init__(self, alias):
        self.alias = alias


class _AliasMgr:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


class _Person:
    def __init__(self, name, aliases):
        self.name = name
        self.aliases = _AliasMgr([_Alias(a) for a in aliases])


class _Keyword:
    def __init__(self, term, weight, applies_to=None, enabled=True):
        self.term = term
        self.weight = weight
        self.applies_to_groups = applies_to or []
        self.enabled = enabled


def _babuji():
    return _Person("Babuji", ["Babuji", "Sri Ramchandra of Shahjahanpur"])


class RuleBasedFilterTests(SimpleTestCase):
    def test_no_alias_match_rejects(self):
        flt = RuleBasedFilter([_Keyword("Sahaj Marg", "hard")])
        r = flt.evaluate(RawHit(url="x", title="cooking recipes"), _babuji(), "A_BABUJI")
        self.assertEqual(r.decision, "reject")
        self.assertEqual(r.score, 0.0)

    def test_alias_plus_hard_keyword_includes(self):
        flt = RuleBasedFilter([_Keyword("Sahaj Marg", "hard"), _Keyword("Shahjahanpur", "hard")])
        r = flt.evaluate(
            RawHit(url="x", title="Babuji on Sahaj Marg in Shahjahanpur"),
            _babuji(),
            "A_BABUJI",
        )
        self.assertEqual(r.decision, "include")
        self.assertGreaterEqual(r.score, 5.0)
        self.assertIn("Babuji", r.matched_aliases)
        self.assertIn("hard:Sahaj Marg", r.matched_keywords)

    def test_uncertain_keyword_surfaces_review(self):
        flt = RuleBasedFilter([_Keyword("Mahatma", "uncertain")])
        r = flt.evaluate(RawHit(url="x", title="Mahatma Babuji speech"), _babuji(), "A_BABUJI")
        self.assertEqual(r.decision, "uncertain")
        self.assertIn("uncertain:Mahatma", r.matched_keywords)

    def test_alias_only_below_threshold_uncertain(self):
        flt = RuleBasedFilter([])
        r = flt.evaluate(RawHit(url="x", title="Random Babuji mention"), _babuji(), "A_BABUJI")
        self.assertEqual(r.decision, "uncertain")
        self.assertIn("Babuji", r.matched_aliases)

    def test_applies_to_groups_scoping(self):
        flt = RuleBasedFilter([_Keyword("Naqshbandi", "hard", applies_to=["C_LINEAGE"])])
        title = "Babuji and the Naqshbandi tradition"
        r_a = flt.evaluate(RawHit(url="x", title=title), _babuji(), "A_BABUJI")
        r_c = flt.evaluate(RawHit(url="x", title=title), _babuji(), "C_LINEAGE")
        self.assertNotIn("hard:Naqshbandi", r_a.matched_keywords)
        self.assertIn("hard:Naqshbandi", r_c.matched_keywords)

    def test_disabled_keyword_ignored(self):
        flt = RuleBasedFilter([_Keyword("Sahaj Marg", "hard", enabled=False)])
        r = flt.evaluate(RawHit(url="x", title="Babuji on Sahaj Marg"), _babuji(), "A_BABUJI")
        self.assertNotIn("hard:Sahaj Marg", r.matched_keywords)

    def test_word_boundary_prevents_substring_match(self):
        flt = RuleBasedFilter([_Keyword("guru", "soft")])
        # "gurus" should NOT match "guru" with word boundary
        r = flt.evaluate(
            RawHit(url="x", title="Babuji and the gurus convention"),
            _babuji(),
            "A_BABUJI",
        )
        self.assertNotIn("soft:guru", r.matched_keywords)

    def test_alias_dedup_does_not_double_count(self):
        person = _Person("Babuji", ["Babuji"])  # Person.name == alias
        flt = RuleBasedFilter([])
        r = flt.evaluate(RawHit(url="x", title="Babuji"), person, "A_BABUJI")
        self.assertEqual(len(r.matched_aliases), 1)
