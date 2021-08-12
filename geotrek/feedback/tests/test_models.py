from django.conf import settings
from django.test.testcases import TestCase
from django.test.utils import override_settings

from geotrek.feedback.factories import ReportFactory


class TestFeedbackModel(TestCase):
    def setUp(self):
        self.report = ReportFactory(email="mail@mail.fr")

    def test_get_display_name(self):
        s = f'<a data-pk=\"{self.report.pk}\" href=\"{self.report.get_detail_url()}\" title="mail@mail.fr">mail@mail.fr</a>'
        self.assertEqual(self.report.name_display, s)

    @override_settings(ALLOWED_HOSTS=["geotrek.local"])
    def test_get_full_url(self):
        s = f"geotrek.local/report/{self.report.pk}/"
        self.assertEqual(self.report.full_url, s)

    @override_settings(ALLOWED_HOSTS=[])
    def test_get_full_url_exception(self):
        with self.assertRaises(Exception):
            self.report.full_url
