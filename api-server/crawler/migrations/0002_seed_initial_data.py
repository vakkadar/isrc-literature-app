from django.db import migrations


GROUP_A = "A_BABUJI"
GROUP_B = "B_LALAJI_DIRECT"
GROUP_C = "C_LINEAGE"


SOURCES = [
    # (code, name, type, applies_to_groups, max_per_term, rate_limit_seconds)
    ("web_ddg", "DuckDuckGo Web", "web", [GROUP_A, GROUP_B, GROUP_C], 10, 2.0),
    ("official_sites", "Heartfulness / SRCM official sites", "official_site", [GROUP_A, GROUP_B], 10, 2.0),
    ("archive_org", "Internet Archive", "archive", [GROUP_A], 15, 1.0),
    ("youtube", "YouTube Data API v3", "youtube", [GROUP_A], 15, 1.0),
    ("google_books", "Google Books", "google_books", [GROUP_A, GROUP_B, GROUP_C], 10, 1.0),
    ("open_library", "OpenLibrary", "open_library", [GROUP_A, GROUP_B, GROUP_C], 10, 1.0),
    ("listen_notes", "Listen Notes Podcasts", "podcast", [GROUP_A], 10, 2.0),
]


KEYWORDS = [
    # (term, weight, applies_to_groups, notes)
    ("Sahaj Marg", "hard", [GROUP_A, GROUP_B], "Lineage name (Babuji's teaching)"),
    ("Heartfulness", "hard", [GROUP_A], "Modern brand of the Babuji lineage"),
    ("Sri Ramchandra Mission", "hard", [GROUP_A, GROUP_B], "Organization founded 1945"),
    ("SRCM", "hard", [GROUP_A, GROUP_B], "Abbreviation for Sri Ramchandra Mission"),
    ("Shahjahanpur", "hard", [GROUP_A], "Babuji's town"),
    ("Fatehgarh", "hard", [GROUP_B, GROUP_C], "Lalaji's town"),
    ("Fategarh", "hard", [GROUP_B, GROUP_C], "Alt spelling of Fatehgarh"),
    ("Naqshbandi", "hard", [GROUP_C], "Sufi order in the predecessor lineage"),
    ("Sufi silsila", "hard", [GROUP_C], "Sufi spiritual lineage"),
    ("Raipur", "hard", [GROUP_C], "Maulvi Fazl Ahmad Khan's town"),
    ("pranahuti", "soft", [], "Yogic transmission"),
    ("transmission", "soft", [], "Spiritual practice term"),
    ("meditation", "soft", [], "General context"),
    ("spirituality", "soft", [], "General context"),
    ("guru", "soft", [], "General context"),
    ("yoga", "soft", [], "General context"),
    ("Mahatma", "uncertain", [], "Title shared with many figures"),
    ("Master", "uncertain", [], "Title shared with many figures"),
]


PERSONS = [
    # (name, lineage_group, aliases=[(alias, language, is_primary), ...])
    (
        "Babuji",
        GROUP_A,
        [
            ("Sri Ramchandra of Shahjahanpur", "en", True),
            ("Shri Ram Chandra of Shahjahanpur", "en", False),
            ("Ramchandra Maharaj", "en", False),
            ("Ram Chandra", "en", False),
        ],
    ),
    (
        "Lalaji",
        GROUP_B,
        [
            ("Sri Ramchandra of Fatehgarh", "en", True),
            ("Mahatma Ram Chandra of Fatehgarh", "en", False),
            ("Lalaji Maharaj", "en", False),
        ],
    ),
    (
        "Maulvi Fazl Ahmad Khan of Raipur",
        GROUP_C,
        [
            ("Fazl Ahmad Khan", "en", True),
            ("Hazrat Maulvi Fazl Ahmad Khan", "en", False),
            ("Raipur Maulvi", "en", False),
        ],
    ),
]


def seed_forward(apps, schema_editor):
    Source = apps.get_model("crawler", "Source")
    DisambiguationKeyword = apps.get_model("crawler", "DisambiguationKeyword")
    PersonAlias = apps.get_model("crawler", "PersonAlias")
    Person = apps.get_model("content", "Person")

    for code, name, type_, groups, cap, rate in SOURCES:
        Source.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "type": type_,
                "enabled": True,
                "applies_to_groups": groups,
                "max_per_term": cap,
                "rate_limit_seconds": rate,
            },
        )

    for term, weight, groups, notes in KEYWORDS:
        DisambiguationKeyword.objects.update_or_create(
            term=term,
            defaults={
                "weight": weight,
                "applies_to_groups": groups,
                "enabled": True,
                "notes": notes,
            },
        )

    for name, group, aliases in PERSONS:
        person, _ = Person.objects.update_or_create(
            name=name,
            defaults={"lineage_group": group, "crawl_active": True},
        )
        for alias, lang, is_primary in aliases:
            PersonAlias.objects.update_or_create(
                person=person,
                alias=alias,
                defaults={"language": lang, "is_primary": is_primary},
            )


def seed_reverse(apps, schema_editor):
    Source = apps.get_model("crawler", "Source")
    DisambiguationKeyword = apps.get_model("crawler", "DisambiguationKeyword")
    PersonAlias = apps.get_model("crawler", "PersonAlias")
    Person = apps.get_model("content", "Person")

    Source.objects.filter(code__in=[s[0] for s in SOURCES]).delete()
    DisambiguationKeyword.objects.filter(term__in=[k[0] for k in KEYWORDS]).delete()
    for name, _group, aliases in PERSONS:
        try:
            p = Person.objects.get(name=name)
        except Person.DoesNotExist:
            continue
        PersonAlias.objects.filter(person=p, alias__in=[a[0] for a in aliases]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("crawler", "0001_initial"),
        ("content", "0003_person_lineage_group_crawl_active"),
    ]

    operations = [
        migrations.RunPython(seed_forward, seed_reverse),
    ]
