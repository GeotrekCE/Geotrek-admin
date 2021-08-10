import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from geotrek.feedback.parsers import SuricateParser
from geotrek.feedback.helpers import SuricateRequestManager

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    leave_locale_alone = True

    def add_arguments(self, parser):
        parser.add_argument(
            "--activities",
            dest="activities",
            action='store_true',
            help="Import activities but no alerts",
            default=False,
        )
        parser.add_argument(
            "--statuses",
            dest="statuses",
            action='store_true',
            help="Import statuses but no alerts",
            default=False,
        )
        parser.add_argument(
            "--test_connection",
            dest="test",
            action='store_true',
            help="Test ability to reach Suricate API",
            default=False,
        )

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        if settings.SURICATE_MANAGEMENT_ENABLED:
            parser = SuricateParser()
            has_no_params = not (options["statuses"] | options["activities"] | options["test"])
            if options['test']:
                SuricateRequestManager().test_suricate_connection()
            else:
                if options["activities"] or has_no_params:
                    parser.get_activities()
                if options["statuses"] or has_no_params:
                    parser.get_statuses()
                if has_no_params:
                    parser.get_alerts(verbosity=verbosity)
        else:
            logger.error("To use this command, please activate setting SURICATE_MANAGEMENT_ENABLED.")
