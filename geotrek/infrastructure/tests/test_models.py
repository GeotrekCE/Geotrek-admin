from django.conf import settings
from django.test import TestCase
from unittest import skipIf

from geotrek.core.tests.factories import PathFactory
from geotrek.infrastructure.tests.factories import InfrastructureFactory
from geotrek.zoning.tests import factories as zoning_factory


class InfrastructureTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city1 = zoning_factory.CityFactory(code='01000', name="city1", geom='SRID=2154;MULTIPOLYGON(((-1 -1, -1 1, 1 1, 1 -1, -1 -1)))')
        cls.city2 = zoning_factory.CityFactory(code='02000', name="city2", geom='SRID=2154;MULTIPOLYGON(((-1 -1, -1 1, 1 1, 1 -1, -1 -1)))')
        cls.city3 = zoning_factory.CityFactory(code='03000', name="city3", geom='SRID=2154;MULTIPOLYGON(((1 1, 1 3, 3 3, 3 1, 1 1)))')

        cls.infra_cities1_2 = InfrastructureFactory.create()
        cls.infra_cities1_2.geom = 'SRID=2154;POINT(0 0)'
        cls.infra_cities1_2.save()

        cls.infra_cities3 = InfrastructureFactory.create()
        cls.infra_cities3.geom = 'SRID=2154;POINT(2 2)'
        cls.infra_cities3.save()

    def test_helpers(self):
        p = PathFactory.create()

        if settings.TREKKING_TOPOLOGY_ENABLED:
            infra = InfrastructureFactory.create(paths=[p])
        else:
            infra = InfrastructureFactory.create(geom=p.geom)

        self.assertCountEqual(p.infrastructures, [infra])

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
    def test_display_cities(self):
        # Case : return 2 cities (not city3, is out of zone)
        self.assertEqual(self.infra_cities1_2.cities_display, "city1, city2")

        # Case : return 1 city (not city3, is out of zone)
        self.city2.delete()
        self.assertEqual(self.infra_cities1_2.cities_display, "city1")

        # Case : return 0 city (not city3, is out of zone)
        self.city1.delete()
        self.assertEqual(self.infra_cities1_2.cities_display, "")

        # Case : return only city3
        self.assertEqual(self.infra_cities3.cities_display, "city3")
