import io
import os
import uuid
from unittest import mock
from unittest.mock import MagicMock

from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from django.urls.base import reverse
from django.utils.translation import gettext_lazy as _
from mapentity.tests.factories import SuperUserFactory, UserFactory

from geotrek.authent.tests.factories import UserProfileFactory
from geotrek.common.models import Attachment
from geotrek.feedback.forms import ReportForm
from geotrek.feedback.helpers import SuricateMessenger, SuricateRequestManager
from geotrek.feedback.models import (AttachedMessage, Report, ReportActivity,
                                     ReportProblemMagnitude, ReportStatus, WorkflowManager)
from geotrek.feedback.tests.factories import (ReportFactory,
                                              ReportStatusFactory,
                                              WorkflowManagerFactory)

SURICATE_REPORT_SETTINGS = {
    "URL": "http://suricate.wsstandard.example.com/",
    "ID_ORIGIN": "geotrek",
    "PRIVATE_KEY_CLIENT_SERVER": "",
    "PRIVATE_KEY_SERVER_CLIENT": "",
    "AUTH": ("", ""),
}

SURICATE_MANAGEMENT_SETTINGS = {
    "URL": "http://suricate.wsmanagement.example.com/",
    "ID_ORIGIN": "geotrek",
    "PRIVATE_KEY_CLIENT_SERVER": "",
    "PRIVATE_KEY_SERVER_CLIENT": "",
    "AUTH": ("", ""),
}

SURICATE_WORKFLOW_SETTINGS = {
    "SURICATE_RELOCATED_REPORT_MESSAGE": "Le Signalement ne concerne pas le Département du Gard - Relocalisé hors du Département"
}


def mocked_json(file_name):
    filename = os.path.join(os.path.dirname(__file__), "data", file_name)
    with open(filename, "r") as f:
        return bytes(f.read(), encoding="UTF-8")


def mocked_image(file_name):
    filename = os.path.join(os.path.dirname(__file__), "data", file_name)
    with open(filename, "rb") as f:
        return bytearray(f.read())


@override_settings(SURICATE_REPORT_SETTINGS=SURICATE_REPORT_SETTINGS)
@override_settings(SURICATE_MANAGEMENT_SETTINGS=SURICATE_MANAGEMENT_SETTINGS)
class SuricateTests(TestCase):
    """Test Suricate API"""

    def build_get_request_patch(self, mocked: MagicMock, cause_JPG_error=False, remove_one_alert=False):
        """Mock get requests to Suricate API"""

        def build_response_patch(url, params=None, **kwargs):
            mock_response = MagicMock()
            if "GetActivities" in url:
                mock_response.status_code = 200
                mock_response.content = mocked_json("suricate_activities.json")
            elif "GetStatusList" in url:
                mock_response.status_code = 200
                mock_response.content = mocked_json("suricate_statuses.json")
            elif "GetAlerts" in url and not remove_one_alert:
                mock_response.content = mocked_json("suricate_alerts.json")
                mock_response.status_code = 200
            elif "GetAlerts" in url and remove_one_alert:
                mock_response.content = mocked_json("suricate_alerts_later.json")
                mock_response.status_code = 200
            elif "wsLockAlert" in url or "wsUnlockAlert" in url or "wsUpdateGPS" in url:
                mock_response.content = mocked_json("suricate_positive.json")
                mock_response.status_code = 200
            elif cause_JPG_error:
                mock_response.status_code = 404
            elif ".jpg" in url or ".png" in url or ".JPG" in url:
                mock_response.content = mocked_image("theme-fauna.png")
                mock_response.status_code = 200
            else:
                mock_response.status_code = 404
            return mock_response

        mocked.side_effect = build_response_patch

    def build_post_request_patch(self, mocked: MagicMock):
        """Mock post requests to Suricate API"""

        def build_response_patch(url, params=None, **kwargs):
            mock_response = MagicMock()
            if "SendReport" in url or "UpdateStatus" in url or "MessageSentinel" in url:
                mock_response.status_code = 200
                mock_response.content = mocked_json(
                    "suricate_positive.json"
                )
            else:
                mock_response.status_code = 404
            return mock_response

        mocked.side_effect = build_response_patch

    def build_failed_request_patch(self, mocked: MagicMock):
        """Mock error responses from Suricate API"""
        mock_response = mock.Mock()
        mock_response.content = mocked_json("suricate_negative.json")
        mock_response.status_code = 400
        mocked.return_value = mock_response

    def build_timeout_request_patch(self, mocked: MagicMock):
        """Mock error responses from Suricate API"""
        mock_response = mock.Mock()
        mock_response.status_code = 408  # reqest timeout
        mock_response.content = {}
        mocked.return_value = mock_response

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        UserProfileFactory.create(user=cls.user)
        cls.workflow_manager = WorkflowManagerFactory(user=cls.user)
        cls.admin = SuperUserFactory(username="Admin", password="drowssap")
        cls.programmed_status = ReportStatusFactory(identifier='programmed', label="Programmé", timer_days=7)

    def setUp(self):
        self.client.force_login(self.admin)


class SuricateAPITests(SuricateTests):

    @override_settings(SURICATE_MANAGEMENT_ENABLED=True)
    @mock.patch("geotrek.feedback.parsers.logger")
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_statuses(self, mocked_get, mocked_logger):
        """Test GET requests on Statuses endpoint creates statuses objects"""
        self.build_get_request_patch(mocked_get)
        call_command("sync_suricate", statuses=True)
        self.assertEqual(ReportStatus.objects.count(), 6)
        mocked_logger.info.assert_called_with("New status - id: classified, label: Classé sans suite")

    @override_settings(SURICATE_MANAGEMENT_ENABLED=True)
    @mock.patch("geotrek.feedback.parsers.logger")
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_activities(self, mocked_get, mocked_logger):
        """Test GET requests on Activities endpoint creates statuses objects"""
        self.build_get_request_patch(mocked_get)
        call_command("sync_suricate", activities=True)
        self.assertEqual(ReportActivity.objects.count(), 32)
        mocked_logger.info.assert_called_with("New activity - id: 51, label: Roller, Skateboard")

    @override_settings(SURICATE_MANAGEMENT_ENABLED=True)
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_activities_and_statuses(self, mocked):
        """Test GET requests on both Activities and Statuses endpoint creates objects"""
        self.build_get_request_patch(mocked)
        call_command("sync_suricate", activities=True, statuses=True)
        self.assertEqual(ReportActivity.objects.count(), 32)
        self.assertEqual(ReportStatus.objects.count(), 6)

    @override_settings(SURICATE_MANAGEMENT_ENABLED=False)
    @mock.patch("geotrek.feedback.management.commands.sync_suricate.logger")
    def test_command_disabled(self, mocked):
        """Test sync_suricate command is disabled when setting is False"""
        call_command("sync_suricate", activities=True, statuses=True)
        mocked.error.assert_called_with("To use this command, please activate setting SURICATE_MANAGEMENT_ENABLED or SURICATE_WORKFLOW_ENABLED.")

    @override_settings(SURICATE_MANAGEMENT_ENABLED=True)
    @mock.patch("geotrek.feedback.parsers.logger")
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_alerts_creates_alerts_and_send_mail(self, mocked_get, mocked_logger):
        """Test GET requests on Alerts endpoint creates alerts and related objects, and sends an email"""
        self.build_get_request_patch(mocked_get, cause_JPG_error=True)
        self.assertEqual(len(mail.outbox), 0)
        call_command("sync_suricate", verbosity=2)
        # 8 out of 9 are imported because one of them is out of bbox by design
        self.assertEqual(Report.objects.count(), 8)
        self.assertEqual(ReportProblemMagnitude.objects.count(), 3)
        self.assertEqual(AttachedMessage.objects.count(), 44)
        self.assertEqual(Attachment.objects.count(), 6)
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject, "[Geotrek] New reports from Suricate")
        self.assertIn("New reports have been imported from Suricate", sent_mail.body)
        self.assertIn("Please consult your reports in Geotrek", sent_mail.body)
        for report in Report.objects.all():
            self.assertIn(report.full_url, sent_mail.body)
        r = Report.objects.all()[0]
        r.category = None
        r.save()
        # Fetch it again to verify 'super.save' was called (management mode)
        r.refresh_from_db()
        self.assertIsNone(r.category)
        # Test new filed report are not assigned to workflow manager when mode is management
        r = Report.objects.get(external_uuid="E7C73347-5056-AA2B-DDBFDCD9328CD742")
        self.assertIsNone(r.assigned_user)
        # Assert no new mail on update
        self.assertEqual(len(mail.outbox), 1)
        # Test sync specific report overwrites local info
        r.comment = ""
        r.save()
        r.refresh_from_db()
        self.assertEquals(r.comment, "")
        call_command("sync_suricate", report=r.pk, verbosity=2)
        r.refresh_from_db()
        self.assertEquals(r.comment, "Ne pas prendre la route Départementale 155 en direction de Malons")
        # Test sync last report overwrites local info
        r = Report.objects.get(external_uuid="7EE5DF25-5056-AA2B-DDBEEFA5768CD53E")
        self.assertEquals(r.comment, "Lames cassées")
        r.comment = ""
        r.save()
        r.refresh_from_db()
        self.assertEquals(r.comment, "")
        call_command("sync_suricate", report=0, verbosity=2)
        r.refresh_from_db()
        self.assertEquals(r.comment, "Lames cassées")

    @override_settings(SURICATE_WORKFLOW_ENABLED=True)
    @mock.patch("geotrek.feedback.parsers.logger")
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_alerts_does_not_override_internal_status(self, mocked_get, mocked_logger):
        # Test sync last report does not override internal status
        self.build_get_request_patch(mocked_get, cause_JPG_error=True)
        call_command("sync_suricate", verbosity=2)
        r = Report.objects.get(external_uuid="7EE5DF25-5056-AA2B-DDBEEFA5768CD53E")
        r.status = self.programmed_status
        r.comment = "I was changed"
        r.save()
        r.refresh_from_db()
        self.assertEquals(r.status.identifier, "programmed")
        call_command("sync_suricate", report=0, verbosity=2)
        r.refresh_from_db()
        # Comment change was overriden, status change was not
        self.assertEquals(r.status.identifier, "programmed")
        self.assertEquals(r.comment, "Lames cassées")

    @override_settings(SURICATE_MANAGEMENT_ENABLED=True)
    @mock.patch("geotrek.feedback.parsers.ContentFile.__init__")
    @mock.patch("geotrek.feedback.parsers.logger")
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_sync_handles_malformed_images(self, mocked_get, mocked_logger, mocked_save):
        self.build_get_request_patch(mocked_get)
        """Test Suricate sync is not interupted by corruped images"""
        mocked_save.side_effect = Exception("This image is bad")
        call_command("sync_suricate", verbosity=2)
        mocked_logger.error.assert_called()

    @override_settings(SURICATE_WORKFLOW_ENABLED=True)
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_alerts_creates_alerts_and_send_mail_and_assign(self, mocked_get):
        """Test GET requests on Alerts endpoint creates alerts and related objects, and sends an email"""
        self.build_get_request_patch(mocked_get, cause_JPG_error=True)
        self.assertEqual(len(mail.outbox), 0)
        call_command("sync_suricate", verbosity=2)
        # 8 out of 9 are imported because one of them is out of bbox by design
        self.assertEqual(Report.objects.count(), 8)
        self.assertEqual(ReportProblemMagnitude.objects.count(), 3)
        self.assertEqual(AttachedMessage.objects.count(), 44)
        self.assertEqual(Attachment.objects.count(), 6)
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject, "[Geotrek] New reports from Suricate")
        # Test update report does not send email and saves
        r = Report.objects.all()[0]
        r.category = None
        r.save()
        # Fetch it again to verify 'super.save' was called (management mode)
        r.refresh_from_db()
        self.assertIsNone(r.category)
        # Test new filed report are assigned to workflow manager
        r = Report.objects.get(external_uuid="E7C73347-5056-AA2B-DDBFDCD9328CD742")
        self.assertIn(r.assigned_user.pk, list(WorkflowManager.objects.values_list('user', flat=True)))
        # Assert no new mail on update
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(SURICATE_MANAGEMENT_ENABLED=True)
    @mock.patch("geotrek.feedback.parsers.logger")
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_failed_attachments_are_downloaded_on_next_sync(self, mocked_get, mocked_logger):
        """Test failed requests to download attachments are retried on next sync"""
        self.assertEqual(Attachment.objects.count(), 0)
        # Fail to download all images
        self.build_get_request_patch(mocked_get, cause_JPG_error=True)
        call_command("sync_suricate", verbosity=2)
        self.assertEqual(Attachment.objects.count(), 6)
        for atta in Attachment.objects.all():
            # All attachments are missing their image file
            self.assertFalse(atta.attachment_file.name)
        # Succesfully download all images
        self.build_get_request_patch(mocked_get, cause_JPG_error=False)
        call_command("sync_suricate", verbosity=2)
        self.assertEqual(Attachment.objects.count(), 6)
        for atta in Attachment.objects.all():
            # No attachments are missing their image file
            self.assertTrue(atta.attachment_file.name)
        # Succesfully download all images a second time to cover "skip file" case
        call_command("sync_suricate", verbosity=2)
        self.assertEqual(Attachment.objects.count(), 6)
        for atta in Attachment.objects.all():
            # No attachments are missing their image file
            self.assertTrue(atta.attachment_file.name)

    @override_settings(PAPERCLIP_ENABLE_LINK=False)
    @override_settings(SURICATE_MANAGEMENT_ENABLED=True)
    def test_sync_needs_paperclip_enabled(self):
        """Test failed requests to download attachments are retried on next sync"""
        with self.assertRaises(Exception):
            call_command("sync_suricate", verbosity=2)

    @override_settings(SURICATE_REPORT_ENABLED=True)
    @override_settings(SURICATE_MANAGEMENT_ENABLED=False)
    @override_settings(SURICATE_REPORT_SETTINGS=SURICATE_REPORT_SETTINGS)
    @mock.patch("geotrek.feedback.helpers.SuricateMessenger.post_report")
    def test_save_on_report_posts_to_suricate_in_report_mode(self, post_report):
        """Test post to suricate on save Report in Suricate Report Mode"""
        report = Report.objects.create()
        post_report.assert_called_once_with(report)

    @override_settings(SURICATE_MANAGEMENT_ENABLED=True)
    @override_settings(SURICATE_REPORT_SETTINGS=SURICATE_REPORT_SETTINGS)
    @mock.patch("geotrek.feedback.helpers.SuricateMessenger.post_report")
    def test_save_on_report_posts_to_suricate_in_management_mode(self, post_report):
        """Test post to suricate on save Report in Suricate Management Mode"""
        # Create a report with an UID - emulates report from Suricate
        uid = uuid.uuid4()
        Report.objects.create(external_uuid=uid)
        post_report.assert_not_called()
        # Create a report with no UID - emulates new report from Geotrek
        report = Report.objects.create(external_uuid=None)
        post_report.assert_called_once_with(report)

    @override_settings(SURICATE_MANAGEMENT_ENABLED=False)
    @override_settings(SURICATE_REPORT_ENABLED=False)
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_save_on_report_doesnt_post_to_suricate_in_no_suricate_mode(self, post_report):
        """Test save does not post to suricate on save Report in No Suricate Mode"""
        Report.objects.create()
        post_report.assert_not_called()

    @mock.patch("geotrek.feedback.helpers.requests.post")
    def test_post_request_to_suricate(self, mock_post):
        """Test post request itself
        Request post is mock
        """
        # Create a report without saving it
        report = ReportFactory.build()

        # Define a mock response
        self.build_post_request_patch(mock_post)

        # Call the function with the report
        result = SuricateMessenger().post_report(report)
        self.assertEqual(result, None)

    @override_settings(SURICATE_MANAGEMENT_ENABLED=False)
    @override_settings(SURICATE_REPORT_SETTINGS=SURICATE_REPORT_SETTINGS)
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_request_to_suricate_fails_1(self, mock_get):
        """Test get request itself fails
        """
        # Mock error 408
        self.build_timeout_request_patch(mock_get)
        # Get raises an exception
        with self.assertRaises(Exception):
            SuricateRequestManager().get_suricate(endpoint="wsGetStatusList")

    @override_settings(SURICATE_MANAGEMENT_ENABLED=False)
    @override_settings(SURICATE_REPORT_SETTINGS=SURICATE_REPORT_SETTINGS)
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_request_to_suricate_fails_2(self, mock_get):
        """Test get request itself fails
        """
        # Mock error 400
        self.build_failed_request_patch(mock_get)
        # Get raises an exception
        with self.assertRaises(Exception):
            SuricateRequestManager().get_suricate(endpoint="wsGetStatusList")

    @override_settings(SURICATE_MANAGEMENT_ENABLED=True)
    @mock.patch("sys.stdout", new_callable=io.StringIO)
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_connection_test(self, mock_get, mocked_stdout):
        """Assert connection test command outputs OK
        """
        # Mock error 408
        self.build_get_request_patch(mock_get)
        call_command("sync_suricate", test=True)
        # Assert outputs OK
        self.assertEquals(mocked_stdout.getvalue(), 'API Standard :\nOK\nAPI Gestion :\nOK\n')

    @override_settings(SURICATE_MANAGEMENT_ENABLED=True)
    @mock.patch("sys.stdout", new_callable=io.StringIO)
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_connection_test_fails_API(self, mock_get, mocked_stdout):
        """Assert connection test command outputs error when it fails on Suricate API side
        """
        # Mock negative response
        self.build_failed_request_patch(mock_get)
        # Assert outputs KO
        call_command("sync_suricate", test=True)
        self.assertEquals(mocked_stdout.getvalue(), "API Standard :\nKO - Status code: 400\nAPI Gestion :\nKO - Status code: 400\n")

    @override_settings(SURICATE_MANAGEMENT_ENABLED=True)
    @mock.patch("sys.stdout", new_callable=io.StringIO)
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_connection_test_fails_HTTP(self, mock_get, mocked_stdout):
        """Assert connection test command outputs error when it fails on HTTP
        """
        # Mock error 408
        self.build_timeout_request_patch(mock_get)
        # Assert outputs KO
        call_command("sync_suricate", test=True)
        self.assertEquals(mocked_stdout.getvalue(), "API Standard :\nKO - Status code: 408\nAPI Gestion :\nKO - Status code: 408\n")

    @override_settings(SURICATE_MANAGEMENT_ENABLED=True)
    @mock.patch("geotrek.feedback.parsers.logger")
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_relocated_report_is_deleted_on_next_sync(self, mocked_get, mocked_logger):
        """Test reports relocated outside of BBOX are deleted on next sync"""
        self.build_get_request_patch(mocked_get, remove_one_alert=False)
        call_command("sync_suricate", verbosity=2)
        # 8 out of 9 are imported because one of them is out of bbox by design
        self.assertEqual(Report.objects.filter(external_uuid="742CBF16-5056-AA2B-DD1FD403F72D6B9B").count(), 1)
        self.assertEqual(Report.objects.count(), 8)
        """Test GET requests on Alerts endpoint creates alerts and related objects, and sends an email"""
        self.build_get_request_patch(mocked_get, remove_one_alert=True)
        call_command("sync_suricate", verbosity=2)
        # One out of the 9 was removed from response because this report now lives outside of BBOX according to Suricate
        # 7 out of 8 are imported because one of them is out of bbox by design
        self.assertEqual(Report.objects.filter(external_uuid="742CBF16-5056-AA2B-DD1FD403F72D6B9B").count(), 0)
        self.assertEqual(Report.objects.count(), 7)


class SuricateInterfaceTests(SuricateTests):

    @override_settings(SURICATE_MANAGEMENT_ENABLED=False)
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_import_from_interface_disabled(self, mocked):
        user = UserFactory.create(username='Slush', password='Puppy')
        self.client.force_login(user)
        self.build_get_request_patch(mocked)
        url = reverse('common:import_dataset')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'import-suricate')
        self.assertNotContains(response, _('Data to import from Suricate'))
        response = self.client.post(
            url, {
                'import-suricate': 'Import',
                'parser': 'everything',
            }
        )
        self.assertEqual(Report.objects.count(), 0)

    @override_settings(SURICATE_MANAGEMENT_ENABLED=True)
    @mock.patch("geotrek.feedback.parsers.SuricateParser.get_alerts")
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_import_from_interface_enabled(self, mocked_get, mocked_parser):
        user = UserFactory.create(username='Slush', password='Puppy')
        self.client.force_login(user)
        # mocked_parser = mock.Mock()
        self.build_get_request_patch(mocked_get)
        url = reverse('common:import_dataset')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'import-suricate')
        self.assertContains(response, _('Data to import from Suricate'))
        response = self.client.post(
            url, {
                'import-suricate': 'Import',
                'parser': 'everything',
            }
        )
        self.assertEqual(response.status_code, 200)
        mocked_parser.assert_called_once()

    @override_settings(SURICATE_MANAGEMENT_ENABLED=False)
    @override_settings(SURICATE_REPORT_SETTINGS=SURICATE_REPORT_SETTINGS)
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_request_to_suricate_fails_1(self, mock_get):
        """Test get request itself fails
        """
        # Mock error 408
        self.build_timeout_request_patch(mock_get)
        # Get raises an exception
        with self.assertRaises(Exception):
            SuricateRequestManager().get_suricate(endpoint="wsGetStatusList")


class SuricateWorkflowTests(SuricateTests):
    fixtures = ['geotrek/maintenance/fixtures/basic.json']

    @classmethod
    def setUpTestData(cls):
        SuricateTests.setUpTestData()
        cls.filed_status = ReportStatusFactory(identifier='filed', label="Déposé")
        cls.classified_status = ReportStatusFactory(identifier='classified', label="Classé sans suite")
        cls.waiting_status = ReportStatusFactory(identifier='waiting', label="En cours", timer_days=6)
        cls.rejected_status = ReportStatusFactory(identifier='rejected', label="Rejeté")
        cls.late_intervention_status = ReportStatusFactory(identifier='late_intervention', label="Intervention en retard")
        cls.late_resolution_status = ReportStatusFactory(identifier='late_resolution', label="Resolution en retard")
        cls.solved_intervention_status = ReportStatusFactory(identifier='solved_intervention', label="Intervention terminée")
        cls.resolved_status = ReportStatusFactory(identifier='solved', label="Résolu")
        cls.report = ReportFactory(status=cls.filed_status, external_uuid=uuid.uuid4())
        cls.admin = SuperUserFactory(username="Admiin", password="drowssap")
        cls.interv_report = ReportFactory(status=cls.programmed_status)


def raise_multiple(exceptions):
    if not exceptions:  # list emptied, recursion ends
        return
    try:
        raise exceptions.pop()  # pop removes list entries
    finally:
        raise_multiple(exceptions)  # recursion


def test_for_all_suricate_modes(test_func):
    def inner(self, *args, **kwargs):
        exceptions = []
        try:
            with override_settings(SURICATE_REPORT_ENABLED=False, SURICATE_MANAGEMENT_ENABLED=False, SURICATE_WORKFLOW_ENABLED=False, LANGUAGE_CODE='fr'):
                test_func(self, *args, **kwargs)
        except AssertionError as e:
            e.args += ("Failed for 'No Suricate' mode",)
            exceptions.append(e)
        try:
            with override_settings(SURICATE_REPORT_ENABLED=True, SURICATE_MANAGEMENT_ENABLED=False, SURICATE_WORKFLOW_ENABLED=False, LANGUAGE_CODE='fr'):
                test_func(self, *args, **kwargs)
        except AssertionError as e:
            e.args += ("Failed for 'Suricate Report' mode",)
            exceptions.append(e)
        try:
            with override_settings(SURICATE_REPORT_ENABLED=True, SURICATE_MANAGEMENT_ENABLED=True, SURICATE_WORKFLOW_ENABLED=False, LANGUAGE_CODE='fr'):
                test_func(self, *args, **kwargs)
        except AssertionError as e:
            e.args += ("Failed for 'Suricate Management' mode",)
            exceptions.append(e)
        try:
            with override_settings(SURICATE_REPORT_ENABLED=False, SURICATE_MANAGEMENT_ENABLED=False, SURICATE_WORKFLOW_ENABLED=True, LANGUAGE_CODE='fr'):
                test_func(self, *args, **kwargs)
        except AssertionError as e:
            e.args += ("Failed for 'Suricate Workflow' mode",)
            exceptions.append(e)
        raise_multiple(exceptions)
    return inner


def test_for_report_and_basic_modes(test_func):
    def inner(self, *args, **kwargs):
        exceptions = []
        try:
            with override_settings(SURICATE_REPORT_ENABLED=False, SURICATE_MANAGEMENT_ENABLED=False, SURICATE_WORKFLOW_ENABLED=False, LANGUAGE_CODE='fr'):
                test_func(self, *args, **kwargs)
        except AssertionError as e:
            e.args += ("Failed for 'No Suricate' mode",)
            exceptions.append(e)
        try:
            with override_settings(SURICATE_REPORT_ENABLED=True, SURICATE_MANAGEMENT_ENABLED=False, SURICATE_WORKFLOW_ENABLED=False, LANGUAGE_CODE='fr'):
                test_func(self, *args, **kwargs)
        except AssertionError as e:
            e.args += ("Failed for 'Suricate Report' mode",)
            exceptions.append(e)
        raise_multiple(exceptions)
    return inner


def test_for_management_and_workflow_modes(test_func):
    def inner(self, *args, **kwargs):
        exceptions = []
        try:
            with override_settings(SURICATE_REPORT_ENABLED=True, SURICATE_MANAGEMENT_ENABLED=True, SURICATE_WORKFLOW_ENABLED=False, LANGUAGE_CODE='fr'):
                test_func(self, *args, **kwargs)
        except AssertionError as e:
            e.args += ("Failed for 'Suricate Management' mode",)
            exceptions.append(e)
        try:
            with override_settings(SURICATE_REPORT_ENABLED=True, SURICATE_MANAGEMENT_ENABLED=True, SURICATE_WORKFLOW_ENABLED=True, LANGUAGE_CODE='fr'):
                test_func(self, *args, **kwargs)
        except AssertionError as e:
            e.args += ("Failed for 'Suricate Workflow' mode",)
        raise_multiple(exceptions)
    return inner


def test_for_workflow_mode(test_func):
    def inner(self, *args, **kwargs):
        try:
            with override_settings(SURICATE_REPORT_ENABLED=True, SURICATE_MANAGEMENT_ENABLED=True, SURICATE_WORKFLOW_ENABLED=True, LANGUAGE_CODE='fr'):
                test_func(self, *args, **kwargs)
        except AssertionError as e:
            e.args += ("Failed for 'Suricate Workflow' mode",)
            raise
    return inner


def test_for_management_mode(test_func):
    def inner(self, *args, **kwargs):
        try:
            with override_settings(SURICATE_REPORT_ENABLED=True, SURICATE_MANAGEMENT_ENABLED=True, SURICATE_WORKFLOW_ENABLED=False, LANGUAGE_CODE='fr'):
                test_func(self, *args, **kwargs)
        except AssertionError as e:
            e.args += ("Failed for 'Suricate Management' mode",)
            raise
    return inner


class TestWorkflowFirstSteps(SuricateWorkflowTests):

    @classmethod
    def setUpTestData(cls):
        SuricateWorkflowTests.setUpTestData()
        cls.report_filed_1 = ReportFactory(status=cls.filed_status, external_uuid=uuid.uuid4(), assigned_user=cls.admin)
        cls.report_filed_2 = ReportFactory(status=cls.filed_status, external_uuid=uuid.uuid4(), assigned_user=cls.admin)

    @override_settings(SURICATE_WORKFLOW_ENABLED=True)
    @mock.patch("geotrek.feedback.helpers.requests.get")
    @mock.patch("geotrek.feedback.helpers.requests.post")
    @mock.patch("geotrek.feedback.helpers.SuricateMessenger.message_sentinel")
    @mock.patch("geotrek.feedback.helpers.SuricateMessenger.update_status")
    def test_classify_alert_notifies_suricate_when_workflow_enabled(self, mocked_notify_suricate_status, mocked_mail_sentinel, mocked_post, mocked_get):
        form = ReportForm(
            instance=self.report_filed_1,
            data={
                'geom': self.report_filed_1.geom,
                'email': self.report_filed_1.email,
                'status': self.classified_status.pk,
                'message_sentinel': "Problème déjà réglé",
                'message_administrators': "Je ne fais rien"
            }
        )
        self.assertTrue(form.is_valid)
        form.save()
        mocked_mail_sentinel.assert_called_once_with(self.report_filed_1.formatted_external_uuid, "Problème déjà réglé")
        mocked_notify_suricate_status.assert_called_once_with(self.report_filed_1.formatted_external_uuid, self.classified_status.identifier, "Problème déjà réglé", "Je ne fais rien")

    @override_settings(SURICATE_WORKFLOW_ENABLED=False)
    @mock.patch("geotrek.feedback.helpers.requests.get")
    @mock.patch("geotrek.feedback.helpers.requests.post")
    @mock.patch("geotrek.feedback.helpers.SuricateMessenger.message_sentinel")
    @mock.patch("geotrek.feedback.helpers.SuricateMessenger.update_status")
    def test_classify_alert_does_not_notify_suricate_when_workflow_disabled(self, mocked_notify_suricate_status, mocked_mail_sentinel, mocked_post, mocked_get):
        form = ReportForm(
            instance=self.report_filed_2,
            data={
                'geom': self.report_filed_2.geom,
                'email': self.report_filed_2.email,
                'status': self.classified_status.pk,
                'message_sentinel': "Problème déjà réglé"
            }
        )
        self.assertTrue(form.is_valid)
        form.save()
        mocked_mail_sentinel.assert_not_called()
        mocked_notify_suricate_status.assert_not_called()
