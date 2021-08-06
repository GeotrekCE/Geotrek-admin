import os
from unittest import mock
from unittest.mock import MagicMock
import uuid

from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from geotrek.feedback.factories import ReportFactory
from geotrek.feedback.helpers import SuricateMessenger
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
}


def mocked_json(file_name):
    filename = os.path.join(os.path.dirname(__file__), "data", file_name)
    with open(filename, "r") as f:
        return bytes(f.read(), encoding="UTF-8")


class SuricateAPITests(TestCase):
    """Test Suricate API"""

    def build_get_request_patch(self, mocked: MagicMock):
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
                mock_response.status_code = 200
                mock_response.content = mocked_json("suricate_alerts.json")
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

    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_statuses(self, mocked):
        """Test GET requests on Statuses endpoint creates statuses objects"""
        self.build_get_request_patch(mocked)
        call_command("sync_suricate", statuses_only=True)
        self.assertEqual(ReportStatus.objects.count(), 5)

    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_activities(self, mocked):
        """Test GET requests on Activities endpoint creates statuses objects"""
        self.build_get_request_patch(mocked)
        call_command("sync_suricate", activities_only=True)
        self.assertEqual(ReportActivity.objects.count(), 32)

    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_get_alerts(self, mocked):
        """Test GET requests on Alerts endpoint creates alerts and related objects"""
        self.build_get_request_patch(mocked)
        call_command("sync_suricate")
        self.assertEqual(Report.objects.count(), 9)
        self.assertEqual(ReportProblemMagnitude.objects.count(), 3)
        self.assertEqual(AttachedMessage.objects.count(), 47)
        # TODO when we can download attachments
        # self.assertEqual(ReportAttachedDocument.objects.count(), 100)
        # self.assertEqual(MessageAttachedDocument.objects.count(), 4)

    @override_settings(SURICATE_REPORT_ENABLED=True)
    @override_settings(SURICATE_REPORT_SETTINGS=SURICATE_REPORT_SETTINGS)
    @mock.patch("geotrek.feedback.helpers.SuricateMessenger.post_report")
    def test_save_on_report_posts_to_suricate(self, post_report):
        """Test post to suricate on save Report"""
        # Create a report with an UID - emulates report from Suricate
        uid = uuid.uuid4()
        Report.objects.create(uid=uid)
        post_report.assert_not_called()
        # Create a report with no UID - emulates new report from Geotrek
        report = Report.objects.create(uid=None)
        post_report.assert_called_once_with(report)

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

    @override_settings(SURICATE_REPORT_ENABLED=True)
    @override_settings(SURICATE_REPORT_SETTINGS=SURICATE_REPORT_SETTINGS)
    @mock.patch("geotrek.feedback.helpers.requests.post")
    def test_request_to_suricate_fails(self, mock_post):
        """Test post request itself but fails
        Request post is mock
        """
        # Define a mock response
        self.build_failed_request_patch(mock_post)

        # Create a report, should raise an excemption
        self.assertRaises(Exception, ReportFactory())
