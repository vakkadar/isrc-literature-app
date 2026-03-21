"""Import content_catalog.json into the Django database."""

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from content.models import Category, Collection, ContentItem, Language, Person

CATALOG_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts" / "content_catalog.json"

LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "fr": "French",
}


class Command(BaseCommand):
    help = "Import scraped content catalog into the database"

    def handle(self, *args, **options):
        if not CATALOG_PATH.exists():
            self.stderr.write(self.style.ERROR(f"Catalog not found: {CATALOG_PATH}"))
            return

        with open(CATALOG_PATH) as f:
            catalog = json.load(f)

        items = catalog["items"]
        self.stdout.write(f"Loading {len(items)} items from catalog...")

        languages = self._create_languages()
        persons = self._create_persons(items)
        categories = self._create_categories(items)
        collections = self._create_collections(items, persons, categories, languages)
        stats = self._create_content_items(items, persons, categories, languages, collections)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("Import complete!"))
        self.stdout.write(f"  Languages:    {len(languages)}")
        self.stdout.write(f"  Persons:      {len(persons)}")
        self.stdout.write(f"  Categories:   {len(categories)}")
        self.stdout.write(f"  Collections:  {len(collections)}")
        self.stdout.write(f"  Content items created:  {stats['created']}")
        self.stdout.write(f"  Content items existing: {stats['existing']}")
        self.stdout.write(f"  Items with files:       {stats['with_file']}")
        self.stdout.write(self.style.SUCCESS("=" * 60))

    def _create_languages(self):
        result = {}
        for code, name in LANGUAGE_MAP.items():
            lang, created = Language.objects.get_or_create(
                code=code, defaults={"name": name}
            )
            result[code] = lang
            if created:
                self.stdout.write(f"  Created language: {name}")
        return result

    def _create_persons(self, items):
        result = {}
        unique_names = sorted(set(item["person"] for item in items))
        for name in unique_names:
            person, created = Person.objects.get_or_create(
                name=name, defaults={"role": Person.Role.MASTER}
            )
            result[name] = person
            if created:
                self.stdout.write(f"  Created person: {name}")
        return result

    def _create_categories(self, items):
        result = {}
        unique_cats = sorted(set(item["category"] for item in items))
        for name in unique_cats:
            slug = slugify(name)
            if not slug:
                slug = "uncategorized"
            cat, created = Category.objects.get_or_create(
                slug=slug, defaults={"name": name}
            )
            result[name] = cat
            if created:
                self.stdout.write(f"  Created category: {name}")
        return result

    def _create_collections(self, items, persons, categories, languages):
        result = {}
        seen = set()
        for item in items:
            hint = item.get("collection_hint")
            if not hint:
                continue
            person_name = item["person"]
            lang_code = item["language"]
            key = (hint, person_name, lang_code)
            if key in seen:
                continue
            seen.add(key)

            person = persons[person_name]
            language = languages.get(lang_code)
            category = categories.get(item["category"])

            coll, created = Collection.objects.get_or_create(
                title=hint,
                person=person,
                language=language,
                defaults={"category": category},
            )
            result[key] = coll
            if created:
                self.stdout.write(f"  Created collection: {hint} ({person_name}, {lang_code})")

        return result

    def _create_content_items(self, items, persons, categories, languages, collections):
        created_count = 0
        existing_count = 0
        with_file = 0

        for item in items:
            person = persons[item["person"]]
            category = categories.get(item["category"])
            language = languages.get(item["language"])

            coll_key = (item.get("collection_hint"), item["person"], item["language"])
            collection = collections.get(coll_key)

            local_path = item.get("local_path", "")
            file_size = item.get("file_size")

            obj, created = ContentItem.objects.get_or_create(
                title=item["title"],
                person=person,
                content_type=item["content_type"],
                source_url=item["source_url"],
                defaults={
                    "collection": collection,
                    "category": category,
                    "language": language,
                    "chapter_number": item.get("chapter_number"),
                    "file": local_path,
                    "file_size_bytes": file_size,
                },
            )

            if created:
                created_count += 1
            else:
                existing_count += 1
                if local_path and not obj.file:
                    obj.file = local_path
                    obj.file_size_bytes = file_size
                    obj.save(update_fields=["file", "file_size_bytes"])

            if obj.file:
                with_file += 1

        return {"created": created_count, "existing": existing_count, "with_file": with_file}
