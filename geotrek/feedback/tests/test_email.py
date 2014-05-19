from django.test import SimpleTestCase
from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend

from geotrek.feedback.factories import ReportFactory


class EmailSendingTest(SimpleTestCase):
    def test_a_mail_is_sent_on_report_creation(self):
        ReportFactory.create()
        self.assertEquals(len(mail.outbox), 1)

    def test_email_format_and_content(self):
        ReportFactory.create(name=u'John Doe',
                             email=u'john.doe@nowhere.com',
                             comment=u'This is a comment')
        sent_mail = mail.outbox[0]
        self.assertEquals(sent_mail.subject,
                          u'[Geotrek] Feedback from John Doe (john.doe@nowhere.com)')
        self.assertIn(u"Comment : This is a comment", sent_mail.body)
        self.assertIn(u"Lat : 1.13 / Lon : 2.26", sent_mail.body)
