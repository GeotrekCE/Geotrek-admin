from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from geotrek.feedback.models import Report
from geotrek.feedback.tests.factories import ReportFactory


class TestRemoveEmailsOlders(TestCase):
    """Test command erase_emails, if older emails are removed"""
    @classmethod
    def setUpTestData(cls):
        cls.recent_report = ReportFactory(email="yeah@you.com")

    def setUp(self):
        # Create two reports
        self.old_report = ReportFactory(email="to_erase@you.com")
        # Modify date_insert for old_report
        one_year_one_day = timezone.timedelta(days=370)
        self.old_report.date_insert = timezone.now() - one_year_one_day
        self.old_report.save()

    def test_erase_old_emails(self):
        output = StringIO()
        call_command('erase_emails', stdout=output)
        old_report = Report.objects.get(id=self.old_report.id)
        self.assertEqual(old_report.email, "")
        self.assertEqual(old_report.__str__(), "Anonymous report")

    def test_dry_run_command(self):
        """Test if dry_run mode keeps emails"""
        output = StringIO()
        call_command('erase_emails', dry_run=True, stdout=output)
        old_report = Report.objects.get(id=self.old_report.id)
        self.assertEqual(old_report.email, "to_erase@you.com")
