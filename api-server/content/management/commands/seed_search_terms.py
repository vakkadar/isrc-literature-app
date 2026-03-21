from django.core.management.base import BaseCommand
from content.models import CrawlerSearchTerm, Person


SEARCH_TERMS = [
    ("Ram Chandra Fatehgarh", "Lalaji"),
    ("Ram Chandra Shahjahanpur", "Babuji"),
    ("Sahaj Marg literature", None),
    ("Babuji letters disciples", "Babuji"),
    ("Lalaji letters", "Lalaji"),
    ("SRCM historical documents", None),
    ("Sahaj Marg preceptor letters", None),
    ("Dr. K.C. Varadachari", "Dr. K.C. Varadachari"),
    ("Kasturi Chaturvedi", "Kasturi Chaturvedi"),
    ("Ishwar Sahai", "Ishwar Sahai"),
    ("Jagmohan Narain", "Jagmohan Narain"),
    ("Brij Mohan Lal", "Brij Mohan Lal"),
    ("Dr. Chaturbhuj Sahai", "Dr. Chaturbhuj Sahai"),
    ("Shri Raghubar Dayal", "Shri Raghubar Dayal"),
    ("Babuji audio recordings", "Babuji"),
    ("Babuji video recordings", "Babuji"),
    ("Sahaj Marg historical audio", None),
    ("Sahaj Marg patrika", None),
    ("Reality at Dawn audio", "Babuji"),
]

PERSON_DEFAULTS = {
    "Lalaji": {"role": Person.Role.MASTER, "description": "Mahatma Ram Chandra ji of Fatehgarh"},
    "Babuji": {"role": Person.Role.MASTER, "description": "Shri Ram Chandra ji of Shahjahanpur"},
    "Dr. K.C. Varadachari": {"role": Person.Role.DISCIPLE, "description": "Disciple of Babuji, philosopher and scholar"},
    "Kasturi Chaturvedi": {"role": Person.Role.DISCIPLE, "description": "Disciple of Babuji"},
    "Ishwar Sahai": {"role": Person.Role.DISCIPLE, "description": "Disciple of Lalaji"},
    "Jagmohan Narain": {"role": Person.Role.DISCIPLE, "description": "Disciple of Lalaji"},
    "Brij Mohan Lal": {"role": Person.Role.DISCIPLE, "description": "Disciple of Lalaji"},
    "Dr. Chaturbhuj Sahai": {"role": Person.Role.DISCIPLE, "description": "Disciple of Lalaji"},
    "Shri Raghubar Dayal": {"role": Person.Role.DISCIPLE, "description": "Disciple of Lalaji"},
}


class Command(BaseCommand):
    help = "Seed the CrawlerSearchTerm table with initial search terms"

    def handle(self, *args, **options):
        person_cache = {}
        created_count = 0

        for term_text, person_name in SEARCH_TERMS:
            person = None
            if person_name:
                if person_name not in person_cache:
                    defaults = PERSON_DEFAULTS.get(person_name, {"role": Person.Role.OTHER})
                    person_cache[person_name], _ = Person.objects.get_or_create(
                        name=person_name, defaults=defaults
                    )
                person = person_cache[person_name]

            _, created = CrawlerSearchTerm.objects.get_or_create(
                term=term_text,
                defaults={"person": person, "enabled": True},
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  Created: {term_text}"))
            else:
                self.stdout.write(f"  Exists:  {term_text}")

        total = CrawlerSearchTerm.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {created_count} new terms created, {total} total terms in database."
        ))
