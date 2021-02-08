from django.conf import settings
from django.test import TestCase

from geotrek.core.factories import PathFactory
from geotrek.core.filters import PathFilterSet
from geotrek.maintenance.factories import ProjectFactory
from geotrek.maintenance.filters import ProjectFilterSet
from geotrek.trekking.factories import TrekFactory
from geotrek.zoning.factories import CityFactory, DistrictFactory, RestrictedAreaFactory


class ProjectYearsFilterTest(TestCase):
    def setUp(self):
        ProjectFactory.create(begin_year=1500, end_year=2000)
        ProjectFactory.create(begin_year=1700, end_year=1800)
        self.filter = ProjectFilterSet()
        self.widget = self.filter.filters['year'].field.widget

    def test_filter_year_with_string(self):
        filter = ProjectFilterSet(data={'year': 'toto'})
        p = ProjectFactory.create(begin_year=1200, end_year=1300)
        self.assertIn(p, filter.qs)
        self.assertEqual(len(filter.qs), 3)
        # We get all project if it's a wrong filter


class ZoningFilterTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geom_1_wkt = 'SRID=2154;MULTIPOLYGON(((200000 300000, 900000 300000, 900000 1200000, 200000 1200000, ' \
                         '200000 300000)))'
        cls.geom_2_wkt = 'SRID=2154;MULTIPOLYGON(((1200000 300000, 1300000 300000, 1300000 1200000, 1200000 1200000, ' \
                         '1200000 300000)))'
        super(ZoningFilterTest, cls).setUpClass()
        cls.city = CityFactory.create(name='city_in', geom=cls.geom_1_wkt)
        cls.city_2 = CityFactory.create(name='city_out', geom=cls.geom_2_wkt)
        cls.district = DistrictFactory.create(name='district_in', geom=cls.geom_1_wkt)
        cls.district_2 = DistrictFactory.create(name='district_out', geom=cls.geom_2_wkt)
        cls.area = RestrictedAreaFactory.create(name='area_in', geom=cls.geom_1_wkt)
        cls.area_2 = RestrictedAreaFactory.create(name='area_out', geom=cls.geom_2_wkt)

    def setUp(self):
        self.city = CityFactory.create(name='test')
        self.district = DistrictFactory.create()
        self.area = RestrictedAreaFactory.create()
        self.path = PathFactory.create(geom='SRID=2154;LINESTRING(200000 300000, 1100000 1200000)')
        if settings.TREKKING_TOPOLOGY_ENABLED:
            self.trek = TrekFactory.create(paths=[self.path], published=False)
        else:
            self.trek = TrekFactory.create(geom='SRID=2154;LINESTRING(200000 300000, 1100000 1200000)', published=False)

    def test_filter_zoning_city(self):
        filter = PathFilterSet(data={'city': self.city.pk})

        self.assertIn(self.path, filter.qs)
        self.assertEqual(len(filter.qs), 1)

        filter = PathFilterSet(data={'city': self.city_2.pk})

        self.assertEqual(len(filter.qs), 0)

    def test_filter_zoning_district(self):
        filter = PathFilterSet(data={'district': self.district.pk})

        self.assertIn(self.path, filter.qs)
        self.assertEqual(len(filter.qs), 1)

        filter = PathFilterSet(data={'district': self.district_2.pk})

        self.assertEqual(len(filter.qs), 0)

    def test_filter_zoning_area(self):
        filter = PathFilterSet(data={'area': self.area.pk})

        self.assertIn(self.path, filter.qs)
        self.assertEqual(len(filter.qs), 1)

        filter = PathFilterSet(data={'area': self.area_2.pk})

        self.assertEqual(len(filter.qs), 0)
