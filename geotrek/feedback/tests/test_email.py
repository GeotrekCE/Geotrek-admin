from unittest import mock

from django.test import TestCase
from django.test.utils import override_settings
from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.utils import translation

from geotrek.feedback.parsers import SuricateParser
from geotrek.feedback.tests.factories import ReportFactory
from geotrek.feedback.tests.test_suricate_sync import SuricateTests


class FailingEmailBackend(BaseEmailBackend):
    """
    This Email Backend is used to test error management when sending email
    """
    def send_messages(self, email_messages):
        raise Exception('Fake problem')


class EmailSendingTest(SuricateTests):
    def test_a_mail_is_sent_on_report_creation(self):
        ReportFactory.create()
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(SURICATE_REPORT_ENABLED=False)
    def test_a_mail_is_not_sent_on_report_modification_no_suricate_mode(self):
        r = ReportFactory.create()
        self.assertEqual(len(mail.outbox), 1)
        r.comment = 'More info about it'
        r.save()
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(SURICATE_REPORT_ENABLED=True)
    @mock.patch("geotrek.feedback.helpers.SuricateMessenger.post_report")
    def test_a_mail_is_not_sent_on_report_modification_suricate_mode(self, post_report):
        r = ReportFactory.create(uid="027b1b63-fa59-48e1-bfdf-daaefc03dee2")
        self.assertEqual(len(mail.outbox), 1)
        r.comment = 'More info about it'
        r.save()
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(EMAIL_BACKEND='geotrek.feedback.tests.FailingEmailBackend')
    def test_email_failure_does_not_prevent_report_creation(self):
        r = ReportFactory.create()
        self.assertEqual(len(mail.outbox), 0)
        self.assertIsNotNone(r.id)

    @override_settings(EMAIL_BACKEND='geotrek.feedback.tests.FailingEmailBackend')
    @mock.patch("geotrek.feedback.models.logger")
    def test_email_failed_logs_and_warns(self, mocked):
        self.assertRaises(Exception, SuricateParser().send_workflow_manager_new_reports_email())
        mocked.error.assert_called_with("Email could not be sent to Workflow Managers.")

    def test_email_format_and_content(self):
        ReportFactory.create(email='john.doe@nowhere.com',
                             comment="This is a 'comment'")
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject,
                         '[Geotrek] Feedback from john.doe@nowhere.com')
        self.assertIn("Comment : This is a 'comment'", sent_mail.body)
        self.assertIn("Lat : 46.500000 / Lon : 3.000000", sent_mail.body)

    @override_settings(LANGUAGE_CODE='fr')
    def test_email_format_and_content_fr(self):
        translation.activate('fr')
        ReportFactory.create(email='jacques.dupont@nulpart.com',
                             comment="Ceci est un commentaire")
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject,
                         '[Geotrek] Signalement de jacques.dupont@nulpart.com')
        self.assertIn("Commentaire : Ceci est un commentaire", sent_mail.body)
        self.assertIn("Lat : 46.500000 / Lon : 3.000000", sent_mail.body)
        self.assertIn("http://www.openstreetmap.org/?mlat=46.500000&mlon=3.000000", sent_mail.body)

        translation.deactivate()
