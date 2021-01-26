from django.conf import settings
from django.test import TestCase

from geotrek.core.factories import PathFactory
from geotrek.trekking.factories import TrekFactory
from geotrek.zoning.factories import CityFactory, DistrictFactory, RestrictedAreaFactory


class ZoningPropertiesMixinTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ZoningPropertiesMixinTest, cls).setUpClass()
        cls.city = CityFactory.create()
        cls.district = DistrictFactory.create()
        cls.area = RestrictedAreaFactory.create()
        cls.path = PathFactory.create(geom='SRID=2154;LINESTRING(200000 300000, 1100000 1200000)')
        if settings.TREKKING_TOPOLOGY_ENABLED:
            cls.trek = TrekFactory.create(paths=[cls.path], published=False)
        else:
            cls.trek = TrekFactory.create(geom='SRID=2154;LINESTRING(200000 300000, 1100000 1200000)', published=False)

    def test_cities(self):
        city = CityFactory.create(published=False)

        self.assertQuerysetEqual(self.path.cities, [repr(city), repr(self.city)], ordered=False)
        self.assertEqual(self.path.cities.count(), 2)
        self.assertQuerysetEqual(self.path.published_cities, [repr(city), repr(self.city)], ordered=False)
        self.assertEqual(self.path.published_cities.count(), 2)

        self.assertQuerysetEqual(self.trek.cities, [repr(city), repr(self.city)], ordered=False)
        self.assertEqual(self.trek.cities.count(), 2)
        self.assertQuerysetEqual(self.trek.published_cities, [repr(self.city)], ordered=False)
        self.assertEqual(self.trek.published_cities.count(), 1)

    def test_districts(self):
        district = DistrictFactory.create(published=False)

        self.assertQuerysetEqual(self.path.districts, [repr(district), repr(self.district)], ordered=False)
        self.assertEqual(self.path.districts.count(), 2)
        self.assertQuerysetEqual(self.path.published_districts, [repr(district), repr(self.district)], ordered=False)
        self.assertEqual(self.path.published_districts.count(), 2)

        self.assertQuerysetEqual(self.trek.districts, [repr(district), repr(self.district)], ordered=False)
        self.assertEqual(self.trek.districts.count(), 2)
        self.assertQuerysetEqual(self.trek.published_districts, [repr(self.district)], ordered=False)
        self.assertEqual(self.trek.published_districts.count(), 1)

    def test_areas(self):
        area = RestrictedAreaFactory.create(published=False)

        self.assertQuerysetEqual(self.path.areas, [repr(area), repr(self.area)], ordered=False)
        self.assertEqual(self.path.areas.count(), 2)
        self.assertQuerysetEqual(self.path.published_areas, [repr(area), repr(self.area)], ordered=False)
        self.assertEqual(self.path.published_areas.count(), 2)

        self.assertQuerysetEqual(self.trek.areas, [repr(area), repr(self.area)], ordered=False)
        self.assertEqual(self.trek.areas.count(), 2)
        self.assertQuerysetEqual(self.trek.published_areas, [repr(self.area)], ordered=False)
        self.assertEqual(self.trek.published_areas.count(), 1)
