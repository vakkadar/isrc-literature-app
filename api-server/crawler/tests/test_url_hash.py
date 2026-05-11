from django.test import SimpleTestCase

from crawler.models import normalize_url, url_hash


class NormalizeURLTests(SimpleTestCase):
    def test_lowercases_scheme_and_host(self):
        self.assertEqual(normalize_url("HTTPS://Example.COM/path"), "https://example.com/path")

    def test_strips_www_prefix(self):
        self.assertEqual(normalize_url("https://www.example.com/p"), "https://example.com/p")

    def test_drops_tracking_params_and_sorts_remaining(self):
        u = "https://example.com/x?utm_source=tw&b=2&a=1&fbclid=xyz"
        self.assertEqual(normalize_url(u), "https://example.com/x?a=1&b=2")

    def test_trailing_slash_canonical(self):
        self.assertEqual(normalize_url("https://example.com/x/"), normalize_url("https://example.com/x"))

    def test_empty_input(self):
        self.assertEqual(normalize_url(""), "")


class URLHashTests(SimpleTestCase):
    def test_hash_is_stable(self):
        h1 = url_hash("https://example.com/p")
        h2 = url_hash("https://EXAMPLE.com/p?utm_source=x")
        self.assertEqual(h1, h2)

    def test_distinct_urls_distinct_hashes(self):
        self.assertNotEqual(url_hash("https://a.com/x"), url_hash("https://a.com/y"))

    def test_hash_is_sha256_hex(self):
        h = url_hash("https://example.com/p")
        self.assertEqual(len(h), 64)
        int(h, 16)  # raises if not hex
