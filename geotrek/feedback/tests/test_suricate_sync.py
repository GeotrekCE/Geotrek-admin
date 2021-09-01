from geotrek.common.models import Attachment
from mapentity.factories import UserFactory
import os
import io
from unittest import mock
from unittest.mock import MagicMock
import uuid

from django.core.management import call_command
from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings
from django.urls.base import reverse
from django.utils.translation import gettext_lazy as _
from geotrek.feedback.factories import ReportFactory
from geotrek.feedback.helpers import SuricateMessenger, SuricateRequestManager
from geotrek.feedback.models import (
    AttachedMessage,
    Report,
    ReportActivity,
    ReportProblemMagnitude,
    ReportStatus,
)

SURICATE_REPORT_SETTINGS = {
    "URL": "http://suricate.example.com",
    "ID_ORIGIN": "geotrek",
    "PRIVATE_KEY_CLIENT_SERVER": "",
    "PRIVATE_KEY_SERVER_CLIENT": "",
    "AUTH": ("", ""),
}

SURICATE_MANAGEMENT_SETTINGS = {
    "URL": "http://suricate.example.com",
    "ID_ORIGIN": "geotrek",
    "PRIVATE_KEY_CLIENT_SERVER": "",
    "PRIVATE_KEY_SERVER_CLIENT": "",
    "AUTH": ("", ""),
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

    def build_get_request_patch(self, mocked: MagicMock, cause_JPG_error=False):
        """Mock get requests to Suricate API"""

        def build_response_patch(url, params=None, **kwargs):
            mock_response = MagicMock()
            if "GetActivities" in url:
                mock_response.status_code = 200
                mock_response.content = mocked_json("suricate_activities.json")
            elif "GetStatusList" in url:
                mock_response.status_code = 200
                mock_response.content = mocked_json("suricate_statuses.json")
            elif "GetAlerts" in url:
                mock_response.content = mocked_json("suricate_alerts.json")
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
            if "SendReport" in url:
                mock_response.status_code = 200
                mock_response.content = mocked_json(
                    "suricate_post_report_positive.json"
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

    def build_extra_failed_request_patch(self, mocked: MagicMock):
        """Mock error responses from Suricate API"""
        mock_response = mock.Mock()
        mock_response.status_code = 408  # reqest timeout
        mock_response.content = {}
        mocked.return_value = mock_response


class SuricateAPITests(SuricateTests):

    @override_settings(SURICATE_MANAGEMENT_ENABLED=True)
    @mock.patch("geotrek.feedback.parsers.logger")
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_statuses(self, mocked_get, mocked_logger):
        """Test GET requests on Statuses endpoint creates statuses objects"""
        self.build_get_request_patch(mocked_get)
        call_command("sync_suricate", statuses=True)
        self.assertEqual(ReportStatus.objects.count(), 5)
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
        self.assertEqual(ReportStatus.objects.count(), 5)

    @override_settings(SURICATE_MANAGEMENT_ENABLED=False)
    @mock.patch("geotrek.feedback.management.commands.sync_suricate.logger")
    def test_command_disabled(self, mocked):
        """Test sync_suricate command is disabled when setting is False"""
        call_command("sync_suricate", activities=True, statuses=True)
        mocked.error.assert_called_with("To use this command, please activate setting SURICATE_MANAGEMENT_ENABLED.")

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
        self.assertEqual(Attachment.objects.count(), 4)
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject, "[Geotrek] New reports from Suricate")
        # Test update report does not send email and saves
        r = Report.objects.all()[0]
        r.category = None
        r.save()
        # Fetch it again to verify 'super.save' was called (management mode)
        r = Report.objects.all()[0]
        self.assertIsNone(r.category)
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
        self.assertEqual(Attachment.objects.count(), 4)
        for atta in Attachment.objects.all():
            # All attachments are missing their image file
            self.assertFalse(atta.attachment_file.name)
        # Succesfully download all images
        self.build_get_request_patch(mocked_get, cause_JPG_error=False)
        call_command("sync_suricate", verbosity=2)
        self.assertEqual(Attachment.objects.count(), 4)
        for atta in Attachment.objects.all():
            # No attachments are missing their image file
            self.assertTrue(atta.attachment_file.name)
        # Succesfully download all images a second time to cover "skip file" case
        call_command("sync_suricate", verbosity=2)
        self.assertEqual(Attachment.objects.count(), 4)
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
        Report.objects.create(uid=uid)
        post_report.assert_not_called()
        # Create a report with no UID - emulates new report from Geotrek
        report = Report.objects.create(uid=None)
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
    @override_settings(SURICATE_REPORT_ENABLED=True)
    @override_settings(SURICATE_REPORT_SETTINGS=SURICATE_REPORT_SETTINGS)
    @mock.patch("geotrek.feedback.helpers.requests.post")
    def test_post_request_to_suricate_fails(self, mock_post):
        """Test post request itself but fails
        Request post is mock
        """
        # Define a mock response
        self.build_failed_request_patch(mock_post)

        # Create a report, should raise an exception
        with self.assertRaises(Exception):
            ReportFactory()

    @override_settings(SURICATE_MANAGEMENT_ENABLED=False)
    @override_settings(SURICATE_REPORT_SETTINGS=SURICATE_REPORT_SETTINGS)
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_request_to_suricate_fails_1(self, mock_get):
        """Test get request itself fails
        """
        # Mock error 408
        self.build_extra_failed_request_patch(mock_get)
        # Get raises an exception
        with self.assertRaises(Exception):
            SuricateRequestManager().get_from_suricate(endpoint="wsGetStatusList")

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
            SuricateRequestManager().get_from_suricate(endpoint="wsGetStatusList")

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
        self.build_extra_failed_request_patch(mock_get)
        # Assert outputs KO
        call_command("sync_suricate", test=True)
        self.assertEquals(mocked_stdout.getvalue(), "API Standard :\nKO - Status code: 408\nAPI Gestion :\nKO - Status code: 408\n")


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
        self.build_extra_failed_request_patch(mock_get)
        # Get raises an exception
        with self.assertRaises(Exception):
            SuricateRequestManager().get_from_suricate(endpoint="wsGetStatusList")
