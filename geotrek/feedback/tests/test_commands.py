from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from geotrek.feedback import factories as feedback_factories


class TestRemoveEmailsOlders(TestCase):
    """Test command erase_emails, if older emails are removed"""

    def setUp(self):
        # Create two reports
        self.old_report = feedback_factories.ReportFactory()
        self.recent_report = feedback_factories.ReportFactory()

        # Modify date_insert for old_report
        one_year_one_day = timezone.timedelta(days=370)
        self.old_report.date_insert = timezone.now() - one_year_one_day
        self.old_report.save()

    def test_erase_old_emails(self):
        output = StringIO()
        call_command('erase_emails', stdout=output, verbosity=2)
        self.assertEqual(self.old_report.email, "")
        self.assertIn('1 email(s) erased', output.getvalue())
