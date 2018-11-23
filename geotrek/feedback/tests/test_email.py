from django.test import TestCase
from django.test.utils import override_settings
from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend

from geotrek.feedback.factories import ReportFactory


class FailingEmailBackend(BaseEmailBackend):
    """
    This Email Backend is used to test error management when sending email
    """
    def send_messages(self, email_messages):
        raise Exception('Fake problem')


class EmailSendingTest(TestCase):
    def test_a_mail_is_sent_on_report_creation(self):
        ReportFactory.create()
        self.assertEqual(len(mail.outbox), 1)

    def test_a_mail_is_not_sent_on_report_modification(self):
        r = ReportFactory.create()
        self.assertEqual(len(mail.outbox), 1)
        r.name = 'toto'
        r.save()
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(EMAIL_BACKEND='geotrek.feedback.tests.FailingEmailBackend')
    def test_email_failure_does_not_prevent_report_creation(self):
        r = ReportFactory.create()
        self.assertEqual(len(mail.outbox), 0)
        self.assertIsNotNone(r.id)

    def test_email_format_and_content(self):
        ReportFactory.create(name='John Doe',
                             email='john.doe@nowhere.com',
                             comment="This is a 'comment'")
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject,
                         '[Geotrek] Feedback from John Doe (john.doe@nowhere.com)')
        self.assertIn("Comment : This is a 'comment'", sent_mail.body)
        self.assertIn("Lat : 46.499999999999936 / Lon : 2.9999999999999996", sent_mail.body)
