import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from geotrek.feedback.helpers import (
    SuricateGestionRequestManager,
    SuricateStandardRequestManager,
)
from geotrek.feedback.parsers import SuricateParser

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    leave_locale_alone = True

    def add_arguments(self, parser):
        parser.add_argument(
            "--activities",
            dest="activities",
            action="store_true",
            help="Import activities but no alerts",
            default=False,
        )
        parser.add_argument(
            "--statuses",
            dest="statuses",
            action="store_true",
            help="Import statuses but no alerts",
            default=False,
        )
        parser.add_argument(
            "--report",
            dest="report",
            action="store",
            help="Import only one report by PK",
            default=None,
        )
        parser.add_argument(
            "--connection-test",
            dest="test",
            action="store_true",
            help="Test ability to reach Suricate API",
            default=False,
        )
        parser.add_argument(
            "--no-notification",
            dest="no_notif",
            action="store_true",
            help="Test ability to reach Suricate API",
            default=False,
        )

    def handle(self, *args, **options):
        verbosity = options["verbosity"]
        if settings.SURICATE_WORKFLOW_ENABLED:
            parser = SuricateParser()
            has_no_params = not (
                options["statuses"] | options["activities"] | options["test"]
            )
            report = options["report"]
            no_notification = options["no_notif"]
            if options["test"]:
                self.test_suricate_connection()
            elif report is not None:
                parser.get_alert(verbosity, report)
            else:
                if options["activities"] or has_no_params:
                    parser.get_activities()
                if options["statuses"] or has_no_params:
                    parser.get_statuses()
                if has_no_params:
                    parser.get_alerts(
                        verbosity=verbosity, should_notify=not (no_notification)
                    )
        else:
            logger.error(
                "To use this command, please activate setting SURICATE_WORKFLOW_ENABLED."
            )

    def test_suricate_connection(self):
        self.stdout.write("API Standard :")
        SuricateStandardRequestManager().test_suricate_connection()
        self.stdout.write("API Gestion :")
        SuricateGestionRequestManager().test_suricate_connection()
