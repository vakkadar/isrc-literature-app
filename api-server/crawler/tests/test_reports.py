from django.core import mail
from django.test import TestCase

from content.models import Person
from crawler.models import CrawlRun, Discovery, Source, url_hash
from crawler.reports import build_digest_context, send_group_digest


class DigestTests(TestCase):
    def setUp(self):
        self.person = Person.objects.create(name="Test Babuji", lineage_group="A_BABUJI")
        self.source = Source.objects.create(code="t_web", name="Test Web", type="web")
        self.run = CrawlRun.objects.create(group="A_BABUJI", status=CrawlRun.Status.SUCCESS)

    def _make_discovery(self, title, score=5.0):
        return Discovery.objects.create(
            run=self.run,
            person=self.person,
            group="A_BABUJI",
            url=f"https://example.com/{title}",
            url_hash=url_hash(f"https://example.com/{title}"),
            title=title,
            source=self.source,
            score=score,
            status=Discovery.Status.NEW,
        )

    def test_build_context_returns_none_when_empty(self):
        self.assertIsNone(build_digest_context(self.run))

    def test_build_context_groups_by_person(self):
        self._make_discovery("Article A")
        self._make_discovery("Article B")
        ctx = build_digest_context(self.run)
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx["total"], 2)
        self.assertIn(self.person.name, ctx["by_person"])
        self.assertEqual(len(ctx["by_person"][self.person.name]), 2)

    def test_send_group_digest_skipped_when_empty(self):
        sent = send_group_digest(self.run)
        self.assertFalse(sent)
        self.assertEqual(len(mail.outbox), 0)

    def test_send_group_digest_emits_one_email_per_run(self):
        self._make_discovery("X")
        sent = send_group_digest(self.run)
        self.assertTrue(sent)
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertIn("Group A", msg.subject)
        self.assertEqual(len(msg.alternatives), 1)
        self.assertEqual(msg.alternatives[0][1], "text/html")
