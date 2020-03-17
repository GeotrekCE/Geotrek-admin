import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from geotrek.feedback.models import Report

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Erase emails older than 1 year from feedbacks."

    def add_arguments(self, parser):
        parser.add_argument('-d', '--days',
                            help="Erase mails older than DAYS (default: %(default)s)",
                            type=int,
                            default=365)
        parser.add_argument('--dry-run',
                            action='store_true',
                            default=False,
                            help="Show only how many reports will be modified")

    def handle(self, *args, **options):
        """Handle method for `erase_email` command"""
        one_year = timezone.now() - timedelta(days=options['days'])
        older_reports = Report.objects.filter(date_insert__lt=one_year).exclude(email='')

        if not options['dry_run']:
            updated_reports = older_reports.update(email='')
            logger.info('{0} email(s) erased'.format(updated_reports,))
        else:
            logger.info('Dry run mode,{0} report(s) should be modified'.format(updated_reports,))
