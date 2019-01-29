import os

from django.test import TestCase
from django.conf import settings
from django.utils.translation import get_language

from geotrek.trekking.factories import TrekFactory
from geotrek.trekking.models import Trek


class AltimetryMixinTest(TestCase):
    def test_get_elevation_chart_none(self):
        trek = TrekFactory.create(no_path=True, published=True)
        response = self.client.get('/media/profiles/trek-%s.png' % trek.pk)
        self.assertEqual(response.status_code, 200)
        # In PDF
        trek.get_elevation_chart_path()
        basefolder = os.path.join(settings.MEDIA_ROOT, 'profiles')
        self.assertTrue(os.listdir(basefolder))
        directory = os.listdir(basefolder)
        self.assertIn(b'%s-%s-%s.png' % (Trek._meta.model_name, str(trek.pk), get_language()), directory)
