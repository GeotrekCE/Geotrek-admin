import logging
from django.core.management.base import BaseCommand
from geotrek.feedback.helpers import SuricateMessenger
from geotrek.feedback.models import PendingEmail, PendingSuricateAPIRequest

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        SuricateMessenger(PendingSuricateAPIRequest).retry_failed_requests()
        for pending_mail in PendingEmail.objects.all():
            pending_mail.retry()
