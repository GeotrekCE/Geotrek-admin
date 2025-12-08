from django.test import TestCase

from geotrek.api.mobile.serializers import common as api_serializers
from geotrek.common.tests.factories import ThemeFactory
from geotrek.trekking.tests.factories import PracticeFactory


class PracticeSerializerTestCase(TestCase):
    def test_practice_with_picto(self):
        practice = PracticeFactory.create(pictogram="a/pictogram/path.png")
        serialized_practice = api_serializers.PracticeSerializer(practice).data
        self.assertEqual(
            serialized_practice["pictogram"], "/media/a/pictogram/path.png"
        )

    def test_practice_with_no_picto(self):
        practice = PracticeFactory.create(pictogram=None)
        serialized_practice = api_serializers.PracticeSerializer(practice).data
        self.assertIsNone(serialized_practice["pictogram"])


class ThemeSerializerTestCase(TestCase):
    def test_theme_with_picto(self):
        theme = ThemeFactory.create(pictogram="a/pictogram/path.png")
        serialized_theme = api_serializers.ThemeSerializer(theme).data
        self.assertEqual(serialized_theme["pictogram"], "/media/a/pictogram/path.png")

    def test_theme_with_no_picto(self):
        theme = ThemeFactory.create(pictogram=None)
        serialized_theme = api_serializers.ThemeSerializer(theme).data
        self.assertIsNone(serialized_theme["pictogram"])
