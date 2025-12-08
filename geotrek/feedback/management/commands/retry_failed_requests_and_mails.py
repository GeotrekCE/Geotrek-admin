import logging

from django.core.management.base import BaseCommand

from geotrek.feedback.helpers import SuricateMessenger
from geotrek.feedback.models import PendingEmail, PendingSuricateAPIRequest

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--flush-all",
            dest="flush",
            action="store_true",
            help="Cancel all pending requests and pending emails",
            default=False,
        )

    def handle(self, *args, **options):
        if options["flush"]:
            SuricateMessenger(PendingSuricateAPIRequest).flush_failed_requests()
            for pending_mail in PendingEmail.objects.all():
                pending_mail.delete()
        else:
            SuricateMessenger(PendingSuricateAPIRequest).retry_failed_requests()
            for pending_mail in PendingEmail.objects.all():
                pending_mail.retry()
