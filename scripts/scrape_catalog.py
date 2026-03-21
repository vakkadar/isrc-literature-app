#!/usr/bin/env python3
"""
Scraper that catalogs all downloadable content from babujisahajmarg.in and
babujishriramchandra.com and produces a JSON manifest without downloading files.
"""

import json
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = SCRIPT_DIR / "content_catalog.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
REQUEST_TIMEOUT = 30
RETRY_DELAY = 3
MAX_RETRIES = 3

AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".wma", ".aac"}
VIDEO_EXTS = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".webm"}
PDF_EXTS = {".pdf"}
ALL_DOWNLOAD_EXTS = AUDIO_EXTS | VIDEO_EXTS | PDF_EXTS

SITE1 = "babujisahajmarg.in"
SITE2 = "babujishriramchandra.com"

# ── Known book titles for collection-hint matching ──────────────────────────
KNOWN_BOOKS = [
    "Reality at Dawn",
    "Commentary on Ten Maxims",
    "Commentary Ten Commandments",
    "Efficacity of Raja Yoga",
    "Efficacy of Raja Yoga",
    "Towards Infinity",
    "Voice Real 1",
    "Voice Real 2",
    "Sahaj Marg Philosophy",
    "Truth Eternal",
    "Role of the Abhyasi",
    "Autobiography of R.C.",
    "Autobiography of Ram Chandra",
    "Messages Eternal",
    "Jewels of Sun",
]

COLLECTION_ALIASES = {
    "Autobiography of Ram Chandra": "Autobiography of R.C.",
}


# ── Helpers ─────────────────────────────────────────────────────────────────

def fetch_page(url: str) -> BeautifulSoup | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return BeautifulSoup(resp.content, "html.parser")
        except requests.RequestException as exc:
            print(f"  [attempt {attempt}/{MAX_RETRIES}] Error fetching {url}: {exc}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    return None


def file_ext(url: str) -> str:
    path = urlparse(url).path
    path = unquote(path)
    return Path(path).suffix.lower()


def classify_content(url: str) -> str:
    ext = file_ext(url)
    if ext in PDF_EXTS:
        return "pdf"
    if ext in AUDIO_EXTS:
        return "audio"
    if ext in VIDEO_EXTS:
        return "video"
    if "youtube.com" in url or "youtu.be" in url:
        return "video"
    return "link"


def clean_title(raw: str) -> str:
    """Turn a filename or heading into a human-readable title."""
    raw = unquote(raw)
    raw = re.sub(r"\.(pdf|mp3|mp4|wav|ogg)$", "", raw, flags=re.I)
    raw = raw.replace("_", " ").replace("-", " ")
    raw = re.sub(r"\s+", " ", raw).strip()
    if raw and raw[0].islower():
        raw = raw[0].upper() + raw[1:]
    return raw


def title_from_url(url: str) -> str:
    path = unquote(urlparse(url).path)
    fname = Path(path).stem
    return clean_title(fname)


def detect_language(page_url: str, file_url: str, title: str) -> str:
    pu = page_url.lower()
    fu = unquote(file_url).lower()
    tl = title.lower()

    if "telugu" in pu or "/telugu/" in fu or "telugu" in tl:
        return "te"
    if "hindi" in pu or "/hindi/" in fu:
        return "hi"
    if "/fr/" in pu or "/fr/" in fu or "french" in tl:
        return "fr"

    if any(ord(c) >= 0x0C00 and ord(c) <= 0x0C7F for c in title):
        return "te"
    if any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in title):
        return "hi"

    return "en"


def detect_person(page_url: str, title: str, category: str) -> str:
    pu = page_url.lower()
    tl = title.lower()

    if "kasturi" in pu or "kasturi" in tl:
        return "Saint Kasturi"
    if "lalaji" in pu or "lalaji" in tl or "lala" in tl:
        return "Lalaji Maharaj"
    if "babuji" in pu or "babuji" in tl or "ram chandra" in tl:
        return "Babuji Maharaj"

    if any(k in pu for k in ("babujibooks", "babujiaudio", "babujienglish", "babujitelugu")):
        return "Babuji Maharaj"
    if "lalajibooks" in pu:
        return "Lalaji Maharaj"
    if "saintkasturi" in pu:
        return "Saint Kasturi"

    return "Babuji Maharaj"


def detect_category(page_url: str, section_heading: str, content_type: str) -> str:
    pu = page_url.lower()
    sh = section_heading.lower()

    if "patrika" in pu or "patrika" in sh:
        return "Patrika"
    if "souvnier" in sh or "souvenir" in sh or "souvniers" in pu:
        return "Souvenirs"
    if "preceptor" in sh or "preceptor" in pu:
        return "Preceptor Guidelines"
    if "q-answer" in pu or "catechism" in sh or "face-to-face" in sh:
        return "Q&A"
    if "letter" in pu:
        return "Letters"
    if "message" in pu:
        return "Messages"
    if "video" in pu:
        return "Videos"
    if "song" in sh or "kasturi" in sh and content_type == "audio":
        return "Songs"

    if content_type == "audio":
        if "audiobook" in pu:
            return "Audio Books"
        if "babujiaudio" in pu:
            return "Speeches"
        return "Audio Books"
    if content_type == "video":
        return "Videos"

    if "esotericism" in pu:
        if "research" in sh:
            return "Research"
        if "gate way" in sh or "gateway" in sh:
            return "Books"
        return "Research"
    if "book" in pu:
        return "Books"

    return "Books"


def extract_chapter_number(filename: str) -> int | None:
    """Try to pull a chapter/track number from the filename."""
    m = re.match(r"^(\d{1,3})[_\-\s.]", filename)
    if m:
        return int(m.group(1))
    m = re.search(r"[_\-](\d{1,3})[_\-]of[_\-]", filename, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"Chapter\s*(\d+)", filename, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"Vol[_\-\s]*(\d+)[_\-\s]*(\d+)[_\-\s]*of", filename, re.I)
    if m:
        return int(m.group(2))
    m = re.search(r"[_\-](\d{2})(?:\.\w+)?$", filename)
    if m:
        return int(m.group(1))
    return None


def guess_collection(title: str, filename: str, section_heading: str,
                     content_type: str = "audio") -> str | None:
    """Group audio chapters that belong to the same book/collection."""
    fn = unquote(filename).lower()

    for book in KNOWN_BOOKS:
        if book.lower().replace(" ", "") in fn.replace(" ", "").replace("-", "").replace("_", ""):
            return COLLECTION_ALIASES.get(book, book)

    if content_type == "audio":
        heading = section_heading.strip()
        if heading:
            heading_clean = re.sub(r"^[eE][_\-\s]*", "", heading).strip()
            heading_clean = clean_title(heading_clean)
            if heading_clean and len(heading_clean) > 2:
                return heading_clean

        base = re.sub(r"[\d_\-]+(?:of[\d_\-]+)?\.mp3$", "", fn, flags=re.I).strip(" -_")
        base = clean_title(base)
        if base and len(base) > 3:
            return base

    if content_type == "pdf":
        return title if title else None

    return None


# ── Site 1: babujisahajmarg.in ──────────────────────────────────────────────

SITE1_PAGES = {
    "https://babujisahajmarg.in/babujibooks-english.html": {
        "default_person": "Babuji Maharaj",
        "default_category": "Books",
        "default_lang": "en",
    },
    "https://babujisahajmarg.in/babujibooks-hindi.html": {
        "default_person": "Babuji Maharaj",
        "default_category": "Books",
        "default_lang": "hi",
    },
    "https://babujisahajmarg.in/babujibooks-telugu.html": {
        "default_person": "Babuji Maharaj",
        "default_category": "Books",
        "default_lang": "te",
    },
    "https://babujisahajmarg.in/lalajibooks.html": {
        "default_person": "Lalaji Maharaj",
        "default_category": "Books",
        "default_lang": "en",
    },
    "https://babujisahajmarg.in/esotericism.html": {
        "default_person": "Babuji Maharaj",
        "default_category": "Research",
        "default_lang": "en",
    },
    "https://babujisahajmarg.in/babujienglishaudiobooks.html": {
        "default_person": "Babuji Maharaj",
        "default_category": "Audio Books",
        "default_lang": "en",
    },
    "https://babujisahajmarg.in/babujiteluguaudiobooks.html": {
        "default_person": "Babuji Maharaj",
        "default_category": "Audio Books",
        "default_lang": "te",
    },
    "https://babujisahajmarg.in/saintkasturiaudiobooks.html": {
        "default_person": "Saint Kasturi",
        "default_category": "Songs",
        "default_lang": "hi",
    },
    "https://babujisahajmarg.in/babujiaudio.html": {
        "default_person": "Babuji Maharaj",
        "default_category": "Speeches",
        "default_lang": "en",
    },
    "https://babujisahajmarg.in/videos.html": {
        "default_person": "Babuji Maharaj",
        "default_category": "Videos",
        "default_lang": "en",
    },
}


def find_section_heading(tag) -> str:
    """Walk backwards/upwards from a tag to find the nearest h2/h3 section heading."""
    for heading_level in ("h3", "h2"):
        prev = tag
        for _ in range(50):
            prev = prev.find_previous(heading_level)
            if prev:
                return prev.get_text(strip=True)
            break
    return ""


def scrape_site1_link_page(url: str, meta: dict) -> list[dict]:
    """Scrape a page that has direct <a> links to downloadable files."""
    print(f"  Scraping {url} ...")
    soup = fetch_page(url)
    if not soup:
        return []

    items = []
    seen_urls = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        if not href:
            continue

        full_url = urljoin(url, href)
        ext = file_ext(full_url)
        is_downloadable = ext in ALL_DOWNLOAD_EXTS
        is_youtube = "youtube.com" in full_url or "youtu.be" in full_url

        if not is_downloadable and not is_youtube:
            continue
        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)

        link_text = a_tag.get_text(strip=True)
        heading = a_tag.find_previous(["h3", "h4", "h5", "h6"])
        heading_text = heading.get_text(strip=True) if heading else ""
        section_heading = find_section_heading(a_tag)

        GENERIC_HEADINGS = {"books", "audio", "videos", "songs", ""}
        if heading_text.lower().strip() in GENERIC_HEADINGS:
            heading_text = ""
        raw_title = heading_text or link_text or title_from_url(full_url)
        title = clean_title(raw_title)
        if not title or title.lower() in ("read now", "download"):
            title = title_from_url(full_url)

        content_type = classify_content(full_url)
        lang = detect_language(url, full_url, title)
        if lang == "en" and meta["default_lang"] != "en":
            lang = meta["default_lang"]

        person = detect_person(url, title, meta["default_category"])
        if person == "Babuji Maharaj" and meta["default_person"] != "Babuji Maharaj":
            person = meta["default_person"]

        category = detect_category(url, section_heading, content_type)
        filename = unquote(Path(urlparse(full_url).path).name)
        chapter = extract_chapter_number(filename)
        collection = guess_collection(title, filename, section_heading, content_type)

        items.append({
            "title": title,
            "source_url": full_url,
            "content_type": content_type,
            "person": person,
            "category": category,
            "language": lang,
            "collection_hint": collection,
            "chapter_number": chapter,
            "source_site": SITE1,
        })

    return items


def scrape_site1_audio_headings(url: str, meta: dict) -> list[dict]:
    """
    Audio pages on babujisahajmarg.in list filenames as h6/h5 headings.
    Some have <a> links, others just text. For the text-only ones we try
    to reconstruct the URL from the known directory pattern.
    """
    print(f"  Scraping (audio headings) {url} ...")
    soup = fetch_page(url)
    if not soup:
        return []

    items_from_links = []
    seen_urls = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        full_url = urljoin(url, href)
        ext = file_ext(full_url)
        is_youtube = "youtube.com" in full_url or "youtu.be" in full_url
        if ext not in ALL_DOWNLOAD_EXTS and not is_youtube:
            continue
        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)

        heading = a_tag.find_previous(["h3", "h4", "h5"])
        heading_text = heading.get_text(strip=True) if heading else ""
        section = find_section_heading(a_tag)
        link_text = a_tag.get_text(strip=True)
        raw_title = heading_text or link_text or title_from_url(full_url)
        title = clean_title(raw_title)
        if not title or title.lower() in ("read now", "download"):
            title = title_from_url(full_url)

        content_type = classify_content(full_url)
        lang = detect_language(url, full_url, title)
        if lang == "en" and meta["default_lang"] != "en":
            lang = meta["default_lang"]
        person = detect_person(url, title, meta["default_category"])
        if person == "Babuji Maharaj" and meta["default_person"] != "Babuji Maharaj":
            person = meta["default_person"]
        category = detect_category(url, section, content_type)
        filename = unquote(Path(urlparse(full_url).path).name)
        chapter = extract_chapter_number(filename)
        collection = guess_collection(title, filename, section, content_type)

        items_from_links.append({
            "title": title,
            "source_url": full_url,
            "content_type": content_type,
            "person": person,
            "category": category,
            "language": lang,
            "collection_hint": collection,
            "chapter_number": chapter,
            "source_site": SITE1,
        })

    for h_tag in soup.find_all(["h5", "h6"]):
        text = h_tag.get_text(strip=True)
        if not text:
            continue
        a_child = h_tag.find("a", href=True)
        if a_child:
            continue

        has_audio_ext = any(text.lower().endswith(e) for e in AUDIO_EXTS)
        looks_like_track = bool(re.match(r"^\d{1,3}[\s_\-]", text))
        if not has_audio_ext and not looks_like_track:
            continue

        if not has_audio_ext:
            text_with_ext = text + ".mp3"
        else:
            text_with_ext = text

        section_heading = find_section_heading(h_tag)
        title = clean_title(text_with_ext)
        content_type = "audio"
        lang = detect_language(url, text_with_ext, title)
        if lang == "en" and meta["default_lang"] != "en":
            lang = meta["default_lang"]
        person = detect_person(url, title, meta["default_category"])
        if person == "Babuji Maharaj" and meta["default_person"] != "Babuji Maharaj":
            person = meta["default_person"]
        category = meta["default_category"]
        chapter = extract_chapter_number(text_with_ext)
        collection = guess_collection(title, text_with_ext, section_heading, "audio")

        constructed_url = f"https://{SITE1}/assests/Audio/{text_with_ext}"

        if constructed_url not in seen_urls:
            seen_urls.add(constructed_url)
            items_from_links.append({
                "title": title,
                "source_url": constructed_url,
                "content_type": content_type,
                "person": person,
                "category": category,
                "language": lang,
                "collection_hint": collection,
                "chapter_number": chapter,
                "source_site": SITE1,
            })

    return items_from_links


def scrape_site1() -> list[dict]:
    print(f"\n{'='*60}")
    print(f"Scraping {SITE1}")
    print(f"{'='*60}")

    all_items = []
    for page_url, meta in SITE1_PAGES.items():
        cat = meta["default_category"]
        if cat in ("Audio Books", "Songs", "Speeches"):
            items = scrape_site1_audio_headings(page_url, meta)
        else:
            items = scrape_site1_link_page(page_url, meta)
        print(f"    -> Found {len(items)} items")
        all_items.extend(items)

    return all_items


# ── Site 2: babujishriramchandra.com ────────────────────────────────────────

SITE2_PAGES = {
    "https://babujishriramchandra.com/en/books.html": {
        "default_person": "Babuji Maharaj",
        "default_category": "Books",
        "default_lang": "en",
    },
    "https://babujishriramchandra.com/en/messages.html": {
        "default_person": "Babuji Maharaj",
        "default_category": "Messages",
        "default_lang": "en",
    },
    "https://babujishriramchandra.com/en/letters.html": {
        "default_person": "Babuji Maharaj",
        "default_category": "Letters",
        "default_lang": "en",
    },
    "https://babujishriramchandra.com/en/q-answers.html": {
        "default_person": "Babuji Maharaj",
        "default_category": "Q&A",
        "default_lang": "en",
    },
    "https://babujishriramchandra.com/en/gallery/audio.html": {
        "default_person": "Babuji Maharaj",
        "default_category": "Speeches",
        "default_lang": "en",
    },
    "https://babujishriramchandra.com/en/kasturien/books.html": {
        "default_person": "Saint Kasturi",
        "default_category": "Books",
        "default_lang": "en",
    },
    "https://babujishriramchandra.com/en/kasturien/messages.html": {
        "default_person": "Saint Kasturi",
        "default_category": "Messages",
        "default_lang": "en",
    },
    "https://babujishriramchandra.com/en/patrika.html": {
        "default_person": "Babuji Maharaj",
        "default_category": "Patrika",
        "default_lang": "en",
    },
}


def scrape_site2_page(url: str, meta: dict) -> list[dict]:
    print(f"  Scraping {url} ...")
    soup = fetch_page(url)
    if not soup:
        return []

    items = []
    seen_urls = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        if not href:
            continue

        full_url = urljoin(url, href)
        ext = file_ext(full_url)

        if ext not in ALL_DOWNLOAD_EXTS:
            continue
        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)

        link_text = ""
        for child in a_tag.children:
            if isinstance(child, str) and child.strip():
                link_text = child.strip()
                break
        if not link_text:
            link_text = a_tag.get_text(strip=True)
        img = a_tag.find("img")
        alt_text = img.get("alt", "").strip() if img else ""
        if img and link_text == alt_text:
            link_text = ""

        sibling_text = ""
        for sib in a_tag.next_siblings:
            if isinstance(sib, str) and sib.strip():
                sibling_text = sib.strip()
                break

        url_title = title_from_url(full_url)
        raw_title = link_text or alt_text or sibling_text or url_title
        if raw_title.lower() in ("download", "", "print", "email"):
            raw_title = url_title
        if len(raw_title) > 80:
            raw_title = url_title
        title = clean_title(raw_title)

        content_type = classify_content(full_url)
        lang = detect_language(url, full_url, title)
        person = meta["default_person"]
        section = find_section_heading(a_tag)
        category = detect_category(url, section, content_type)
        if category == "Books" and meta["default_category"] != "Books":
            category = meta["default_category"]

        filename = unquote(Path(urlparse(full_url).path).name)
        chapter = extract_chapter_number(filename)
        collection = guess_collection(title, filename, "", content_type)

        if "souvenir" in title.lower() or "birthday" in title.lower() or "b.bd" in filename.lower():
            category = "Souvenirs"
        if "patrika" in filename.lower():
            category = "Patrika"
            collection = "Patrika"

        items.append({
            "title": title,
            "source_url": full_url,
            "content_type": content_type,
            "person": person,
            "category": category,
            "language": lang,
            "collection_hint": collection,
            "chapter_number": chapter,
            "source_site": SITE2,
        })

    return items


def scrape_site2() -> list[dict]:
    print(f"\n{'='*60}")
    print(f"Scraping {SITE2}")
    print(f"{'='*60}")

    all_items = []
    for page_url, meta in SITE2_PAGES.items():
        items = scrape_site2_page(page_url, meta)
        print(f"    -> Found {len(items)} items")
        all_items.extend(items)

    return all_items


# ── De-duplication & output ─────────────────────────────────────────────────

def deduplicate(items: list[dict]) -> list[dict]:
    """Remove exact URL duplicates; keep both sites but normalize collection hints."""
    seen = {}
    deduped = []
    for item in items:
        url = item["source_url"]
        if url in seen:
            continue
        seen[url] = True
        deduped.append(item)
    return deduped


def compute_stats(items: list[dict]) -> dict:
    by_type = Counter(i["content_type"] for i in items)
    by_person = Counter(i["person"] for i in items)
    by_category = Counter(i["category"] for i in items)
    by_site = Counter(i["source_site"] for i in items)
    by_lang = Counter(i["language"] for i in items)

    return {
        "total_items": len(items),
        "by_type": dict(by_type.most_common()),
        "by_person": dict(by_person.most_common()),
        "by_category": dict(by_category.most_common()),
        "by_site": dict(by_site.most_common()),
        "by_language": dict(by_lang.most_common()),
    }


def print_summary(stats: dict):
    print(f"\n{'='*60}")
    print("CATALOG SUMMARY")
    print(f"{'='*60}")
    print(f"Total items cataloged: {stats['total_items']}")

    print(f"\nBy content type:")
    for k, v in stats["by_type"].items():
        print(f"  {k:12s} {v:>5d}")

    print(f"\nBy person:")
    for k, v in stats["by_person"].items():
        print(f"  {k:20s} {v:>5d}")

    print(f"\nBy category:")
    for k, v in stats["by_category"].items():
        print(f"  {k:25s} {v:>5d}")

    print(f"\nBy source site:")
    for k, v in stats["by_site"].items():
        print(f"  {k:35s} {v:>5d}")

    print(f"\nBy language:")
    for k, v in stats["by_language"].items():
        print(f"  {k:5s} {v:>5d}")


def main():
    print("Starting content catalog scraper...")
    print(f"Output will be written to: {OUTPUT_FILE}")

    all_items = []
    all_items.extend(scrape_site1())
    all_items.extend(scrape_site2())

    print(f"\nTotal items before dedup: {len(all_items)}")
    all_items = deduplicate(all_items)
    print(f"Total items after dedup:  {len(all_items)}")

    stats = compute_stats(all_items)

    catalog = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "sources": [SITE1, SITE2],
        "items": all_items,
        "stats": stats,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"\nCatalog written to {OUTPUT_FILE}")
    print_summary(stats)

    return 0


if __name__ == "__main__":
    sys.exit(main())
