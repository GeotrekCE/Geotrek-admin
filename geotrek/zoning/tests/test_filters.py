import datetime

from django.conf import settings
from django.test import TestCase
from django.views.generic.dates import timezone_today

from geotrek.core.filters import PathFilterSet
from geotrek.core.tests.factories import PathFactory
from geotrek.trekking.tests.factories import TrekFactory
from geotrek.zoning.choices import Practicability
from geotrek.zoning.filters import VigilanceAreaFilterSet
from geotrek.zoning.models import VigilanceArea
from geotrek.zoning.tests.factories import (
    CityFactory,
    DistrictFactory,
    RestrictedAreaFactory,
    RestrictedAreaTypeFactory,
    VigilanceAreaFactory,
    VigilanceAreaTypeFactory,
    VigilanceLevelFactory,
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


class VigilanceAreaFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.today = timezone_today()
        cls.yesterday = cls.today - datetime.timedelta(days=1)
        cls.tomorrow = cls.today + datetime.timedelta(days=1)
        cls.area_type = VigilanceAreaTypeFactory.create()
        cls.vigilance_level = VigilanceLevelFactory.create()
        cls.va = VigilanceAreaFactory.create(
            name="Alpha Area",
            vigilance_area_type=cls.area_type,
            vigilance_level=cls.vigilance_level,
            start_date=cls.yesterday,
            end_date=cls.tomorrow,
            practicability=Practicability.PRACTICABLE,
            published=True,
        )

    def test_filter_by_name(self):
        qs = VigilanceArea.objects.all()
        f = VigilanceAreaFilterSet(data={"name": "Alpha"}, queryset=qs)
        self.assertIn(self.va, f.qs)
        f = VigilanceAreaFilterSet(data={"name": "Beta"}, queryset=qs)
        self.assertNotIn(self.va, f.qs)

    def test_filter_by_practicability(self):
        qs = VigilanceArea.objects.all()
        f = VigilanceAreaFilterSet(
            data={"practicability": Practicability.PRACTICABLE}, queryset=qs
        )
        self.assertIn(self.va, f.qs)
        f = VigilanceAreaFilterSet(
            data={"practicability": Practicability.NOT_PRACTICABLE}, queryset=qs
        )
        self.assertNotIn(self.va, f.qs)

    def test_filter_by_vigilance_level(self):
        qs = VigilanceArea.objects.all()
        f = VigilanceAreaFilterSet(
            data={"vigilance_level": [self.vigilance_level.pk]}, queryset=qs
        )
        self.assertIn(self.va, f.qs)

    def test_filter_by_vigilance_area_type(self):
        qs = VigilanceArea.objects.all()
        f = VigilanceAreaFilterSet(
            data={"vigilance_area_type": [self.area_type.pk]}, queryset=qs
        )
        self.assertIn(self.va, f.qs)

    def test_filter_by_period_active(self):
        qs = VigilanceArea.objects.all()
        f = VigilanceAreaFilterSet(data={"period_active": "true"}, queryset=qs)
        self.assertIn(self.va, f.qs)

    def test_filter_by_dates(self):
        qs = VigilanceArea.objects.all()
        f = VigilanceAreaFilterSet(
            data={"before": self.today + datetime.timedelta(days=2)}, queryset=qs
        )
        self.assertIn(self.va, f.qs)
        f = VigilanceAreaFilterSet(
            data={"after": self.tomorrow + datetime.timedelta(days=5)}, queryset=qs
        )
        self.assertNotIn(self.va, f.qs)

    def test_filter_by_vigilance_area_practicability(self):
        from geotrek.zoning.filters import (
            IntersectionFilterVigilanceAreaPracticability,
        )

        qs = VigilanceArea.objects.all()
        fltr = IntersectionFilterVigilanceAreaPracticability()
        self.assertEqual(fltr.filter(qs, None), qs)
        self.assertEqual(fltr.filter(qs, []), qs)
        self.assertEqual(len(fltr.filter(qs, [Practicability.PRACTICABLE])), 1)

    def test_filter_by_vigilance_area(self):
        from geotrek.zoning.filters import (
            IntersectionFilterVigilanceArea,
        )

        qs = VigilanceArea.objects.all()
        fltr = IntersectionFilterVigilanceArea()
        self.assertEqual(fltr.filter(qs, None), qs)
        self.assertEqual(fltr.filter(qs, []), qs)
        self.assertEqual(len(fltr.filter(qs, [self.va])), 1)
