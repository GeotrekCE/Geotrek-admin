from django.test import TestCase

from geotrek.common.templatetags.geotrek_tags import duration
from geotrek.common.tests import TranslationResetMixin


class DurationTagTestCase(TranslationResetMixin, TestCase):
    def test_duration_lt_1h(self):
        self.assertEqual("15 min", duration(0.25))
        self.assertEqual("30 min", duration(0.5))

    def test_duration_lt_1day(self):
        self.assertEqual("1 h", duration(1))
        self.assertEqual("1 h 45", duration(1.75))
        self.assertEqual("3 h 30", duration(3.5))
        self.assertEqual("4 h", duration(4))
        self.assertEqual("6 h", duration(6))
        self.assertEqual("10 h", duration(10))

    def test_duration_gte_1day(self):
        self.assertEqual("1 day", duration(24))
        self.assertEqual("2 days", duration(32))
        self.assertEqual("2 days", duration(48))
        self.assertEqual("3 days", duration(49))
        self.assertEqual("8 days", duration(24 * 8))
        self.assertEqual("9 days", duration(24 * 9))
