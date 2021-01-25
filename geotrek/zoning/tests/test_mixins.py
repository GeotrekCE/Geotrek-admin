from django.conf import settings
from django.test import TestCase

from geotrek.core.factories import PathFactory
from geotrek.trekking.factories import TrekFactory
from geotrek.zoning.factories import CityFactory, DistrictFactory, RestrictedAreaFactory


class ZoningPropertiesMixinTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ZoningPropertiesMixinTest, cls).setUpClass()
        cls.city = CityFactory.create(name="???")
        cls.district = DistrictFactory.create()
        cls.area = RestrictedAreaFactory.create()
        cls.path = PathFactory.create(geom='SRID=2154;LINESTRING(200000 300000, 1100000 1200000)')
        if settings.TREKKING_TOPOLOGY_ENABLED:
            cls.trek = TrekFactory.create(paths=[cls.path], published=False)
        else:
            cls.trek = TrekFactory.create(geom='SRID=2154;LINESTRING(200000 300000, 1100000 1200000)', published=False)

    def test_cities(self):
        city = CityFactory.create(published=False)

        self.assertEqual(self.path.cities.first(), self.city)
        self.assertEqual(self.path.cities.count(), 2)
        self.assertEqual(self.path.published_cities.first(), self.city)
        self.assertEqual(self.path.published_cities.count(), 2)

        self.assertEqual(self.trek.cities.last(), city)
        self.assertEqual(self.trek.cities.count(), 2)
        self.assertEqual(self.trek.published_cities.last(), self.city)
        self.assertEqual(self.trek.published_cities.count(), 1)

    def test_districts(self):
        district = DistrictFactory.create(published=False)

        self.assertEqual(self.path.districts.first(), self.district)
        self.assertEqual(self.path.districts.count(), 2)
        self.assertEqual(self.path.published_districts.first(), self.district)
        self.assertEqual(self.path.published_districts.count(), 2)

        self.assertEqual(self.trek.districts.last(), district)
        self.assertEqual(self.trek.districts.count(), 2)
        self.assertEqual(self.trek.published_districts.last(), self.district)
        self.assertEqual(self.trek.published_districts.count(), 1)

    def test_areas(self):
        area = RestrictedAreaFactory.create(published=False)

        self.assertEqual(self.path.areas.first(), self.area)
        self.assertEqual(self.path.areas.count(), 2)
        self.assertEqual(self.path.published_areas.first(), self.area)
        self.assertEqual(self.path.published_areas.count(), 2)

        self.assertEqual(self.trek.areas.last(), area)
        self.assertEqual(self.trek.areas.count(), 2)
        self.assertEqual(self.trek.published_areas.last(), self.area)
        self.assertEqual(self.trek.published_areas.count(), 1)
