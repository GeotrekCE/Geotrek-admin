from django.conf import settings
from django.test import TestCase

from geotrek.core.tests.factories import PathFactory
from geotrek.trekking.tests.factories import TrekFactory
from geotrek.zoning.tests.factories import (
    CityFactory,
    DistrictFactory,
    RestrictedAreaFactory,
)


class ZoningPropertiesMixinTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.geom_1_wkt = (
            "SRID=2154;MULTIPOLYGON(((200000 300000, 900000 300000, 900000 1200000, 200000 1200000, "
            "200000 300000)))"
        )
        cls.geom_2_wkt = (
            "SRID=2154;MULTIPOLYGON(((900000 300000, 1100000 300000, 1100000 1200000, 900000 1200000, "
            "900000 300000)))"
        )
        cls.city = CityFactory.create(geom=cls.geom_1_wkt)
        cls.district = DistrictFactory.create(geom=cls.geom_1_wkt)
        cls.area = RestrictedAreaFactory.create(geom=cls.geom_1_wkt)

    def setUp(self) -> None:
        self.path = PathFactory.create(
            geom="SRID=2154;LINESTRING(200000 300000, 1100000 1200000)"
        )
        if settings.TREKKING_TOPOLOGY_ENABLED:
            self.trek = TrekFactory.create(paths=[self.path], published=False)
        else:
            self.trek = TrekFactory.create(
                geom="SRID=2154;LINESTRING(200000 300000, 1100000 1200000)",
                published=False,
            )

    def test_cities(self):
        city = CityFactory.create(published=False, geom=self.geom_2_wkt)

        self.assertListEqual(
            [c.name for c in self.path.cities], [self.city.name, city.name]
        )
        self.assertEqual(len(self.path.cities), 2)
        self.assertListEqual(
            [c.name for c in self.path.published_cities], [self.city.name, city.name]
        )
        self.assertEqual(len(self.path.published_cities), 2)

        self.assertListEqual(
            [c.name for c in self.trek.cities], [self.city.name, city.name]
        )
        self.assertEqual(len(self.trek.cities), 2)
        self.assertListEqual(
            [c.name for c in self.trek.published_cities],
            [self.city.name],
        )
        self.assertEqual(len(self.trek.published_cities), 1)

        # Check reverse order
        self.path.reverse()
        self.path.save()

        self.assertListEqual(
            [c.name for c in self.path.cities], [city.name, self.city.name]
        )
        self.assertEqual(len(self.path.cities), 2)
        self.assertListEqual(
            [c.name for c in self.path.published_cities], [city.name, self.city.name]
        )
        self.assertEqual(len(self.path.published_cities), 2)

    def test_districts(self):
        district = DistrictFactory.create(published=False, geom=self.geom_2_wkt)

        self.assertListEqual(
            [d.name for d in self.path.districts], [self.district.name, district.name]
        )
        self.assertEqual(len(self.path.districts), 2)
        self.assertListEqual(
            [d.name for d in self.path.published_districts],
            [self.district.name, district.name],
        )
        self.assertEqual(len(self.path.published_districts), 2)

        self.assertListEqual(
            [d.name for d in self.trek.districts], [self.district.name, district.name]
        )
        self.assertEqual(len(self.trek.districts), 2)
        self.assertListEqual(
            [d.name for d in self.trek.published_districts], [self.district.name]
        )
        self.assertEqual(len(self.trek.published_districts), 1)

        # Check reverse order
        self.path.reverse()
        self.path.save()

        self.assertListEqual(
            [d.name for d in self.path.published_districts],
            [district.name, self.district.name],
        )
        self.assertEqual(len(self.path.districts), 2)
        self.assertListEqual(
            [d.name for d in self.path.published_districts],
            [district.name, self.district.name],
        )
        self.assertEqual(len(self.path.published_districts), 2)

    def test_areas(self):
        area = RestrictedAreaFactory.create(published=False, geom=self.geom_2_wkt)

        self.assertListEqual([a.pk for a in self.path.areas], [self.area.pk, area.pk])
        self.assertEqual(len(self.path.areas), 2)

        self.assertListEqual(
            [a.pk for a in self.path.published_areas], [self.area.pk, area.pk]
        )
        self.assertEqual(len(self.path.published_areas), 2)

        self.assertListEqual([a.pk for a in self.trek.areas], [self.area.pk, area.pk])
        self.assertEqual(len(self.trek.areas), 2)

        self.assertListEqual([a.pk for a in self.trek.published_areas], [self.area.pk])
        self.assertEqual(len(self.trek.published_areas), 1)

        # Check reverse order
        self.path.reverse()
        self.path.save()

        self.assertListEqual([a.pk for a in self.path.areas], [area.pk, self.area.pk])
        self.assertEqual(len(self.path.areas), 2)
        self.assertListEqual(
            [a.pk for a in self.path.published_areas], [area.pk, self.area.pk]
        )
        self.assertEqual(len(self.path.published_areas), 2)
