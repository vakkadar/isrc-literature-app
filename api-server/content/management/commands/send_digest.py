from django.core.management.base import BaseCommand

from content.models import Discovery


class Command(BaseCommand):
    help = "Send a digest email for all pending discoveries"

    def add_arguments(self, parser):
        parser.add_argument(
            "--since-days",
            type=int,
            default=7,
            help="Include discoveries from the last N days (default: 7)",
        )

    def handle(self, *args, **options):
        from django.utils import timezone
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(days=options["since_days"])
        discoveries = list(
            Discovery.objects.filter(
                status=Discovery.Status.PENDING,
                discovered_at__gte=cutoff,
            ).select_related("person_mentioned")
        )

        if not discoveries:
            self.stdout.write("No pending discoveries to send.")
            return

        self.stdout.write(f"Found {len(discoveries)} pending discoveries.")

        from content.management.commands.run_crawler import send_digest_email

        try:
            send_digest_email(discoveries)
            self.stdout.write(self.style.SUCCESS("Digest email sent."))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Failed to send email: {exc}"))
