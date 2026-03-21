#!/usr/bin/env python3
"""Download all content files from the scraped catalog into organized directories."""

import json
import os
import re
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CATALOG_PATH = SCRIPT_DIR / "content_catalog.json"
MEDIA_ROOT = PROJECT_ROOT / "api-server" / "media" / "content"

TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 5
DELAY_BETWEEN = 1


def sanitize_filename(title: str, ext: str) -> str:
    name = re.sub(r'[^\w\s\-.]', '', title)
    name = re.sub(r'\s+', '_', name.strip())
    name = name[:200]
    if not name:
        name = "untitled"
    if not name.lower().endswith(f".{ext}"):
        name = f"{name}.{ext}"
    return name


def get_extension(content_type: str, url: str) -> str:
    ext_map = {"pdf": "pdf", "audio": "mp3", "video": "mp4"}
    url_lower = url.lower().split("?")[0]
    for e in ["pdf", "mp3", "mp4", "wav", "ogg", "flac", "m4a", "webm", "mkv", "avi"]:
        if url_lower.endswith(f".{e}"):
            return e
    return ext_map.get(content_type, "bin")


def create_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_DELAY,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": "ISRC-Literature-Downloader/1.0",
    })
    return session


def download_file(session: requests.Session, url: str, dest: Path) -> int:
    resp = session.get(url, timeout=TIMEOUT, stream=True, allow_redirects=True)
    resp.raise_for_status()
    size = 0
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            size += len(chunk)
    return size


def main():
    with open(CATALOG_PATH) as f:
        catalog = json.load(f)

    items = catalog["items"]
    total = len(items)
    print(f"Found {total} items in catalog")

    session = create_session()
    downloaded = 0
    skipped = 0
    failed = 0

    for i, item in enumerate(items, 1):
        title = item["title"]
        url = item["source_url"]
        ctype = item["content_type"]
        lang = item["language"]

        ext = get_extension(ctype, url)
        filename = sanitize_filename(title, ext)
        rel_dir = Path("content") / ctype / lang
        dest_dir = MEDIA_ROOT.parent / rel_dir
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / filename

        local_path = f"media/{rel_dir}/{filename}"
        item["local_path"] = local_path

        if dest.exists() and dest.stat().st_size > 0:
            item["file_size"] = dest.stat().st_size
            skipped += 1
            print(f"Skipping [{i}/{total}] {title} (already exists)")
            continue

        print(f"Downloading [{i}/{total}] {title}...")

        try:
            size = download_file(session, url, dest)
            item["file_size"] = size
            downloaded += 1
            print(f"  -> {size:,} bytes saved to {filename}")
        except Exception as e:
            failed += 1
            item.pop("local_path", None)
            if dest.exists():
                dest.unlink()
            print(f"  -> FAILED: {e}")

        if i < total:
            time.sleep(DELAY_BETWEEN)

    with open(CATALOG_PATH, "w") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Download complete!")
    print(f"  Downloaded: {downloaded}")
    print(f"  Skipped:    {skipped}")
    print(f"  Failed:     {failed}")
    print(f"  Total:      {total}")
    print(f"Catalog updated with local_path fields.")


if __name__ == "__main__":
    main()
