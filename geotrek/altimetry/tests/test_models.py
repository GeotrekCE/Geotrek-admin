import os

from django.test import TestCase
from django.conf import settings

from geotrek.trekking.factories import TrekFactory
from geotrek.trekking.models import Trek


class AltimetryMixinTest(TestCase):
    def test_get_elevation_chart_none(self):
        trek = TrekFactory.create(no_path=True)
        trek.get_elevation_chart_path()
        basefolder = os.path.join(settings.MEDIA_ROOT, 'profiles')
        self.assertTrue(os.path.exists(os.path.join(basefolder,
                                                    '%s-%s-%s.png' % (Trek._meta.model_name, '1', 'en'))))
