from django.test import SimpleTestCase

from crawler.sources import (
    REGISTRY,
    ArchiveOrgSource,
    BaseSource,
    GoogleBooksSource,
    ListenNotesSource,
    OfficialSiteSource,
    OpenLibrarySource,
    SourceError,
    WebSource,
    YouTubeSource,
    get_source,
)


class _FakeSourceModel:
    def __init__(self, code, config=None, rate=0.0):
        self.code = code
        self.config = config or {}
        self.rate_limit_seconds = rate


class RegistryTests(SimpleTestCase):
    def test_all_expected_codes_registered(self):
        expected = {
            "web_ddg",
            "official_sites",
            "archive_org",
            "youtube",
            "google_books",
            "open_library",
            "listen_notes",
        }
        self.assertEqual(set(REGISTRY.keys()), expected)

    def test_each_class_is_basesource_subclass(self):
        for cls in REGISTRY.values():
            self.assertTrue(issubclass(cls, BaseSource))

    def test_get_source_returns_correct_class(self):
        mapping = {
            "web_ddg": WebSource,
            "official_sites": OfficialSiteSource,
            "archive_org": ArchiveOrgSource,
            "youtube": YouTubeSource,
            "google_books": GoogleBooksSource,
            "open_library": OpenLibrarySource,
            "listen_notes": ListenNotesSource,
        }
        for code, expected_cls in mapping.items():
            instance = get_source(_FakeSourceModel(code))
            self.assertIsInstance(instance, expected_cls)

    def test_get_source_unknown_code_raises(self):
        with self.assertRaises(SourceError):
            get_source(_FakeSourceModel("does_not_exist"))
