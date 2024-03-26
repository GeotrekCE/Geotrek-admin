from django.test import TestCase

from geotrek.common.serializers import HDViewPointGeoJSONSerializer
from geotrek.trekking.tests.factories import TrekFactory

from .factories import HDViewPointFactory


class HDViewPointSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.trek = TrekFactory()
        cls.vp = HDViewPointFactory(content_object=cls.trek)

    def test_geojson_serializer(self):
        serializer = HDViewPointGeoJSONSerializer(instance=self.vp)
        coords = serializer.data.get('geometry').get('coordinates')
        geom_transformed = self.vp.geom.transform(4326, clone=True)
        self.assertAlmostEqual(coords[0], geom_transformed.x)
        self.assertAlmostEqual(coords[1], geom_transformed.y)
