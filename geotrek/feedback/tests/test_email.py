from unittest import mock
from django.conf import settings

from django.test.utils import override_settings
from django.core import mail, management
from django.core.mail.backends.base import BaseEmailBackend
from geotrek.feedback.models import AttachedMessage, PendingEmail, WorkflowManager

from geotrek.feedback.parsers import SuricateParser
from geotrek.feedback.tests.factories import ReportFactory
from geotrek.feedback.tests.test_suricate_sync import SuricateTests


class FailingEmailBackend(BaseEmailBackend):
    """
    This Email Backend is used to test error management when sending email
    """
    def send_messages(self, email_messages):
        raise Exception('Fake problem')


class FailingEmailBackend2(BaseEmailBackend):
    """
    This Email Backend is used to test error management when sending email
    """
    def send_messages(self, email_messages):
        raise Exception('Fake problem 2')


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
        r = ReportFactory.create(external_uuid="027b1b63-fa59-48e1-bfdf-daaefc03dee2")
        self.assertEqual(len(mail.outbox), 1)
        r.comment = 'More info about it'
        r.save()
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(EMAIL_BACKEND='geotrek.feedback.tests.test_email.FailingEmailBackend')
    def test_email_failure_does_not_prevent_report_creation(self):
        r = ReportFactory.create()
        self.assertEqual(len(mail.outbox), 0)
        self.assertIsNotNone(r.id)

    @override_settings(EMAIL_BACKEND='geotrek.feedback.tests.test_email.FailingEmailBackend')
    @mock.patch("geotrek.feedback.models.logger")
    def test_email_failed_warns_and_is_stored_as_pending(self, mocked):
        self.assertRaises(Exception, SuricateParser().send_workflow_manager_new_reports_email(set()))
        mocked.error.assert_called_with("Email could not be sent to Workflow Managers.")
        self.assertEqual(PendingEmail.objects.count(), 1)
        pending_mail = PendingEmail.objects.first()
        self.assertEqual(pending_mail.recipient, WorkflowManager.objects.first().user.email)
        self.assertEqual(pending_mail.subject, "[Geotrek] New reports from Suricate")
        self.assertEqual(pending_mail.error_message, "('Fake problem',)")

    def test_email_format_and_content(self):
        ReportFactory.create(email='john.doe@nowhere.com',
                             comment="This is a 'comment'")
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject,
                         '[Geotrek] Feedback from john.doe@nowhere.com')
        self.assertIn("Comment : This is a 'comment'", sent_mail.body)
        self.assertIn("Lat : 46.500000 / Lon : 3.000000", sent_mail.body)


class TestPendingEmail(SuricateTests):
    @mock.patch("geotrek.feedback.models.logger")
    def test_email_failing_for_manager(self, mocked):
        # Email fails the first time
        with override_settings(EMAIL_BACKEND='geotrek.feedback.tests.test_email.FailingEmailBackend'):
            self.assertRaises(Exception, SuricateParser().send_workflow_manager_new_reports_email(set()))
            mocked.error.assert_called_with("Email could not be sent to Workflow Managers.")
            self.assertEqual(PendingEmail.objects.count(), 1)
            pending_mail = PendingEmail.objects.first()
            self.assertEqual(pending_mail.recipient, WorkflowManager.objects.first().user.email)
            self.assertEqual(pending_mail.retries, 0)
            self.assertEqual(pending_mail.error_message, "('Fake problem',)")
        # Email fails a second time
        with override_settings(EMAIL_BACKEND='geotrek.feedback.tests.test_email.FailingEmailBackend2'):
            management.call_command('retry_failed_requests_and_mails')
            self.assertEqual(PendingEmail.objects.count(), 1)
            pending_mail.refresh_from_db()
            self.assertEqual(pending_mail.recipient, WorkflowManager.objects.first().user.email)
            self.assertEqual(pending_mail.retries, 1)
            self.assertEqual(pending_mail.error_message, "('Fake problem 2',)")
        # Email succeeds at second retry
        management.call_command('retry_failed_requests_and_mails')
        self.assertEqual(PendingEmail.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.to, [WorkflowManager.objects.first().user.email])
        self.assertEqual(sent_mail.subject, "[Geotrek] New reports from Suricate")

    @mock.patch("geotrek.feedback.models.logger")
    def test_email_failing_for_assigned_user(self, mocked):
        report = ReportFactory.create(email='john.doe@nowhere.com',
                                      comment="This is a 'comment'",
                                      assigned_user=self.user)
        # Email fails the first time
        with override_settings(EMAIL_BACKEND='geotrek.feedback.tests.test_email.FailingEmailBackend'):
            self.assertRaises(Exception, report.notify_assigned_user("A nice and useful message"))
            mocked.error.assert_called_with("Email could not be sent to report's assigned user.")
            self.assertEqual(PendingEmail.objects.count(), 1)
            report.refresh_from_db()
            self.assertEqual(1, report.mail_errors)
            pending_mail = PendingEmail.objects.first()
            self.assertEqual(pending_mail.recipient, report.assigned_user.email)
            self.assertEqual(pending_mail.subject, "[Geotrek] New report to process")
            self.assertEqual(pending_mail.retries, 0)
            self.assertEqual(pending_mail.error_message, "('Fake problem',)")
            self.assertEqual(AttachedMessage.objects.filter(report=report).count(), 0)
        # Email fails a second time
        with override_settings(EMAIL_BACKEND='geotrek.feedback.tests.test_email.FailingEmailBackend2'):
            management.call_command('retry_failed_requests_and_mails')
            self.assertEqual(PendingEmail.objects.count(), 1)
            report.refresh_from_db()
            self.assertEqual(1, report.mail_errors)
            pending_mail.refresh_from_db()
            self.assertEqual(pending_mail.recipient, report.assigned_user.email)
            self.assertEqual(pending_mail.retries, 1)
            self.assertEqual(pending_mail.subject, "[Geotrek] New report to process")
            self.assertEqual(pending_mail.error_message, "('Fake problem 2',)")
        # Email succeeds at second retry
        management.call_command('retry_failed_requests_and_mails')
        self.assertEqual(PendingEmail.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 2)
        sent_mail = mail.outbox[1]
        self.assertEqual(sent_mail.to, [report.assigned_user.email])
        self.assertEqual(sent_mail.subject, "[Geotrek] New report to process")
        self.assertIn("A nice and useful message", sent_mail.body)
        report.refresh_from_db()
        self.assertEqual(0, report.mail_errors)
        self.assertEqual(AttachedMessage.objects.filter(report=report).count(), 1)
        attached = AttachedMessage.objects.filter(report=report).first()
        self.assertEqual(attached.author, settings.DEFAULT_FROM_EMAIL + " to " + report.assigned_user.email)
        self.assertIn("You have been assigned a report on Geotrek", attached.content)
