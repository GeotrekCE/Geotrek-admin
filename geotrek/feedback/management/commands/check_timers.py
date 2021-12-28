import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from geotrek.feedback.helpers import test_suricate_connection
from geotrek.feedback.models import TimerEvent
from geotrek.feedback.parsers import SuricateParser

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        for event in TimerEvent.objects.all():
            event.notify_if_needed()
            if event.is_obsolete():
                event.delete()
