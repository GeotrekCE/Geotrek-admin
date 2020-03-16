import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from geotrek.feedback.models import Report

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Erase emails older than 1 year from feedbacks."

    # def add_arguments(self, parser):
    #     parser.add_argument('sample', nargs='+')

    def handle(self, *args, **options):
        one_year = timezone.now() - timedelta(days=365)
        older_reports = Report.objects.filter(date_insert__lt=one_year).exclude(email='')
        updated_reports = older_reports.update(email='')

        logger.info('{0} email(s) erased'.format(updated_reports,))
