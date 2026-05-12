import logging

from django.core.management.base import BaseCommand

from geotrek.feedback.models import TimerEvent

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for event in TimerEvent.objects.all():
            event.notify_if_needed()
            if event.is_obsolete():
                event.delete()
