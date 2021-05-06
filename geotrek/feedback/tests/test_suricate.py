import os
from unittest import mock
from unittest.mock import MagicMock

from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from geotrek.feedback.factories import ReportFactory
from geotrek.feedback.helpers import post_report_to_suricate
from geotrek.feedback.models import (
    AttachedMessage,
    MessageAttachedDocument,
    Report,
    ReportActivity,
    ReportAttachedDocument,
    ReportProblemMagnitude,
    ReportStatus,
)

SURICATE_REPORT_SETTINGS = {
    "URL": "http://suricate.example.com",
    "ID_ORIGIN": "geotrek",
    "PRIVATE_KEY_CLIENT_SERVER": "",
    "PRIVATE_KEY_SERVER_CLIENT": "",
}


def mocked_json(file_name):
    filename = os.path.join(os.path.dirname(__file__), "data", file_name)
    with open(filename, "r") as f:
        return bytes(f.read(), encoding="UTF-8")


class SuricateAPITest(TestCase):
    """Test Suricate API"""

    def build_request_patch(self, mocked: MagicMock):
        def build_response_patch(url, params=None, **kwargs):
            mock_response = MagicMock()
            if "GetActivities" in url:
                mock_response.status_code = 200
                mock_response.content = mocked_json("suricate_activities.json")
            elif "GetStatusList" in url:
                mock_response.status_code = 200
                mock_response.content = mocked_json("suricate_statuses.json")
            elif "GetAlerts" in url:
                mock_response.status_code = 200
                mock_response.content = mocked_json("suricate_alerts.json")
            else:
                mock_response.status_code = 404
            return mock_response

        mocked.side_effect = build_response_patch

    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_statuses(self, mocked):
        self.build_request_patch(mocked)
        call_command("sync_suricate", statuses_only=True)
        self.assertEqual(ReportStatus.objects.count(), 5)

    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_activities(self, mocked):
        self.build_request_patch(mocked)
        call_command("sync_suricate", activities_only=True)
        self.assertEqual(ReportActivity.objects.count(), 32)

    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_alerts(self, mocked):
        self.build_request_patch(mocked)
        call_command("sync_suricate")
        self.assertEqual(Report.objects.count(), 82)
        self.assertEqual(ReportProblemMagnitude.objects.count(), 3)
        self.assertEqual(AttachedMessage.objects.count(), 198)
        self.assertEqual(ReportAttachedDocument.objects.count(), 100)
        self.assertEqual(MessageAttachedDocument.objects.count(), 4)


class OldSuricateTests(TestCase):
    @override_settings(SURICATE_REPORT_ENABLED=True)
    @override_settings(SURICATE_REPORT_SETTINGS=SURICATE_REPORT_SETTINGS)
    @mock.patch("geotrek.feedback.models.post_report_to_suricate")
    def test_save_report_post_to_suricate(self, mock_post_report_to_suricate):
        """Test post to suricate on save Report
        Helper `post_report_to_suricate` function is mock
        """
        # Create a report
        report = ReportFactory()

        # Assert post_report_to_suricate is called
        mock_post_report_to_suricate.assert_called_once_with(report)

    @mock.patch("geotrek.feedback.helpers.requests.post")
    def test_post_request_to_suricate(self, mock_post):
        """Test post request itself
        Request post is mock
        """
        # Create a report without saving it
        report = ReportFactory.build()

        # Define a mock response
        mock_response = mock.Mock()
        expected_dict = {
            "code_ok": "true",
            "check": "515996edc2da463424f4c6e21e19352f ",
            "message": "Merci d’avoir remonté ce problème, nos services vont traiter votre signalement.",
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200

        # Define response for the fake API
        mock_post.return_value = mock_response

        # Call the function with the report
        result = post_report_to_suricate(report)
        self.assertEqual(result, None)

    @override_settings(SURICATE_REPORT_ENABLED=True)
    @override_settings(SURICATE_REPORT_SETTINGS=SURICATE_REPORT_SETTINGS)
    @mock.patch("geotrek.feedback.helpers.requests.post")
    def test_post_request_to_suricate_fails(self, mock_post):
        """Test post request itself but fails
        Request post is mock
        """
        # Define a mock response
        mock_response = mock.Mock()
        expected_dict = {
            "code_ok": "false",
            "error": {"code": "400", "message": "Erreur inconnue."},
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 400

        # Define response for the fake API
        mock_post.return_value = mock_response

        # Create a report, should raise an excemption
        self.assertRaises(Exception, ReportFactory())
