from unittest import mock

from django.test import TestCase
from django.test.utils import override_settings

from geotrek.feedback.factories import ReportFactory
from geotrek.feedback.helpers import post_report_to_suricate

SURICATE_REPORT_SETTINGS = {
    'URL': 'http://suricate.example.com',
    'ID_ORIGIN': 'geotrek',
    'PRIVATE_KEY_CLIENT_SERVER': '',
    'PRIVATE_KEY_SERVER_CLIENT': '',
}


class SuricateAPITest(TestCase):
    """Test Suricate API"""

    @override_settings(SURICATE_REPORT_ENABLED=True)
    @override_settings(SURICATE_REPORT_SETTINGS=SURICATE_REPORT_SETTINGS)
    @mock.patch('geotrek.feedback.models.post_report_to_suricate')
    def test_save_report_post_to_suricate(self, mock_post_report_to_suricate):
        """Test post to suricate on save Report
        Helper `post_report_to_suricate` function is mock
        """
        # Create a report
        report = ReportFactory()

        # Assert post_report_to_suricate is called
        mock_post_report_to_suricate.assert_called_once_with(report)

    @mock.patch('geotrek.feedback.helpers.requests.post')
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
            "message": "Merci d’avoir remonté ce problème, nos services vont traiter votre signalement."
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
    @mock.patch('geotrek.feedback.helpers.requests.post')
    def test_post_request_to_suricate_fails(self, mock_post):
        """Test post request itself but fails
        Request post is mock
        """
        # Define a mock response
        mock_response = mock.Mock()
        expected_dict = {
            "code_ok": "false",
            "error": {
                "code": "400",
                "message": "Erreur inconnue."
            }
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 400

        # Define response for the fake API
        mock_post.return_value = mock_response

        # Create a report, should raise an excemption
        self.assertRaises(Exception, ReportFactory())
