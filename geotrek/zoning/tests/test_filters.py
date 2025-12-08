from django.conf import settings
from django.test import TestCase

from geotrek.core.filters import PathFilterSet
from geotrek.core.tests.factories import PathFactory
from geotrek.trekking.tests.factories import TrekFactory
from geotrek.zoning.tests.factories import (
    CityFactory,
    DistrictFactory,
    RestrictedAreaFactory,
    RestrictedAreaTypeFactory,
)


class ZoningFilterTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.geom_1_wkt = (
            "SRID=2154;MULTIPOLYGON(((200000 300000, 900000 300000, 900000 1200000, 200000 1200000, "
            "200000 300000)))"
        )
        cls.geom_2_wkt = (
            "SRID=2154;MULTIPOLYGON(((1200000 300000, 1300000 300000, 1300000 1200000, 1200000 1200000, "
            "1200000 300000)))"
        )
        cls.city = CityFactory.create(name="city_in", geom=cls.geom_1_wkt)
        cls.city_2 = CityFactory.create(name="city_out", geom=cls.geom_2_wkt)
        cls.district = DistrictFactory.create(name="district_in", geom=cls.geom_1_wkt)
        cls.district_2 = DistrictFactory.create(
            name="district_out", geom=cls.geom_2_wkt
        )
        cls.area = RestrictedAreaFactory.create(name="area_in", geom=cls.geom_1_wkt)
        cls.area_2 = RestrictedAreaFactory.create(name="area_out", geom=cls.geom_2_wkt)
        cls.area_type_3 = RestrictedAreaTypeFactory.create()

        cls.path = PathFactory.create(
            geom="SRID=2154;LINESTRING(200000 300000, 1100000 1200000)"
        )
        if settings.TREKKING_TOPOLOGY_ENABLED:
            cls.trek = TrekFactory.create(paths=[cls.path], published=False)
        else:
            cls.trek = TrekFactory.create(
                geom="SRID=2154;LINESTRING(200000 300000, 1100000 1200000)",
                published=False,
            )

    def test_filter_zoning_city(self):
        filter = PathFilterSet(
            data={
                "city": [
                    self.city,
                ]
            }
        )

        self.assertIn(self.path, filter.qs)
        self.assertEqual(len(filter.qs), 1)

        filter = PathFilterSet(
            data={
                "city": [
                    self.city_2,
                ]
            }
        )

        self.assertEqual(len(filter.qs), 0)

    def test_filter_zoning_district(self):
        filter = PathFilterSet(
            data={
                "district": [
                    self.district,
                ]
            }
        )

        self.assertIn(self.path, filter.qs)
        self.assertEqual(len(filter.qs), 1)

        filter = PathFilterSet(
            data={
                "district": [
                    self.district_2,
                ]
            }
        )

        self.assertEqual(len(filter.qs), 0)

    def test_filter_zoning_area_type(self):
        filter = PathFilterSet(
            data={
                "area_type": [
                    self.area.area_type,
                ]
            }
        )

        self.assertIn(self.path, filter.qs)
        self.assertEqual(len(filter.qs), 1)

        filter = PathFilterSet(
            data={
                "area_type": [
                    self.area_2.area_type,
                ]
            }
        )

        self.assertEqual(len(filter.qs), 0)

        filter = PathFilterSet(
            data={
                "area_type": [
                    self.area_type_3,
                ]
            }
        )

        self.assertEqual(len(filter.qs), 0)
