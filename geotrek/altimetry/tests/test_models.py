import os

from django.conf import settings
from django.test import TestCase
from django.utils.translation import get_language

from geotrek.trekking.models import Trek
from geotrek.trekking.tests.factories import TrekFactory


class AltimetryMixinTest(TestCase):
    def test_get_elevation_chart_none(self):
        trek = TrekFactory.create(published=True)
        response = self.client.get(f"/media/profiles/trek-{trek.pk}.png")
        self.assertEqual(response.status_code, 200)
        # In PDF
        trek.get_elevation_chart_path()
        basefolder = os.path.join(settings.MEDIA_ROOT, "profiles")
        self.assertTrue(os.listdir(basefolder))
        directory = os.listdir(basefolder)
        self.assertIn(
            f"{Trek._meta.model_name}-{str(trek.pk)}-{get_language()}.png",
            directory,
        )
