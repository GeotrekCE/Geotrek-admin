from django.test.testcases import TestCase
from django.test.utils import override_settings
from django.utils.translation import gettext as _

from geotrek.feedback.tests.factories import ReportFactory


class TestFeedbackModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.report = ReportFactory(email="mail@mail.fr")

    def test_get_display_name(self):
        s = f'<a data-pk=\"{self.report.pk}\" href=\"{self.report.get_detail_url()}\" title=\"{_("Report")} n°{self.report.pk}\">{_("Report")} n°{self.report.pk}</a>'
        self.assertEqual(self.report.name_display, s)

    @override_settings(ALLOWED_HOSTS=["geotrek.local"])
    def test_get_full_url(self):
        s = f"geotrek.local/report/{self.report.pk}/"
        self.assertEqual(self.report.full_url, s)
