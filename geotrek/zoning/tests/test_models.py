import datetime
from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import LineString, MultiPolygon, Point, Polygon
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.views.generic.dates import timezone_today

from geotrek.core.tests.factories import PathFactory
from geotrek.signage.tests.factories import SignageFactory
from geotrek.zoning.models import (
    City,
    District,
    RestrictedArea,
    VigilanceArea,
)
from geotrek.zoning.tests.factories import (
    CityFactory,
    DistrictFactory,
    RestrictedAreaFactory,
    RestrictedAreaTypeFactory,
    VigilanceAreaFactory,
    VigilanceAreaTypeFactory,
)


class ZoningLayersUpdateTest(TestCase):
    def test_paths_link(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (1, 1)))
        p2 = PathFactory.create(geom=LineString((1, 1), (3, 3)))
        p3 = PathFactory.create(geom=LineString((3, 3), (4, 4)))
        p4 = PathFactory.create(geom=LineString((4, 1), (6, 2), (4, 3)))

        c1 = CityFactory(
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 4), (0, 4), (0, 0)), srid=settings.SRID)
            ),
        )
        CityFactory(
            geom=MultiPolygon(
                Polygon(((2, 0), (5, 0), (5, 4), (2, 4), (2, 0)), srid=settings.SRID)
            ),
        )

        # There should be automatic link after insert
        self.assertEqual(len(p1.cities), 1)
        self.assertEqual(len(p2.cities), 2)
        self.assertEqual(len(p3.cities), 1)
        self.assertEqual(len(p4.cities), 1)

        c1.geom = MultiPolygon(
            Polygon(((1.5, 0), (2, 0), (2, 4), (1.5, 4), (1.5, 0)), srid=settings.SRID)
        )
        c1.save()

        # Links should have been updated after geom update
        self.assertEqual(len(p1.cities), 0)
        self.assertEqual(len(p2.cities), 2)
        self.assertEqual(len(p3.cities), 1)
        self.assertEqual(len(p4.cities), 1)

        c1.delete()

        # Links should have been updated after delete
        self.assertEqual(len(p1.cities), 0)
        self.assertEqual(len(p2.cities), 1)
        self.assertEqual(len(p3.cities), 1)
        self.assertEqual(len(p4.cities), 1)

    def test_city_with_path_ends_on_border(self):
        """
                 |    |
                 |p1  |p2
                 |    |
        +--------+----+---+
        |                 |
        |                 | City
        |                 |
        +-----------------+
        """
        # Create a path before city to test one trigger
        p1 = PathFactory(geom=LineString((1, 1), (1, 2)))
        CityFactory(
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)), srid=settings.SRID)
            ),
        )
        # Create a path after city to the the another trigger
        p2 = PathFactory(geom=LineString((1.5, 2), (1.5, 1)))
        self.assertEqual(len(p1.cities), 1)
        self.assertEqual(len(p2.cities), 1)

    def test_city_with_topo(self):
        """
        +-----------------+
        |        S        |
        |    +---x---+    |
        |    |       |    | City
        |    |p      |    |
        |    O       O    |
        |                 |
        +-----------------+
        """
        CityFactory(
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)), srid=settings.SRID)
            ),
        )
        if settings.TREKKING_TOPOLOGY_ENABLED:
            p = PathFactory(
                geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5))
            )
            signage = SignageFactory.create(paths=[(p, 0.5, 0.5)])
        else:
            signage = SignageFactory.create(geom=Point(1, 1.5, srid=settings.SRID))
        self.assertEqual(len(signage.cities), 1)

    def test_city_with_topo_2(self):
        """
                 S
             +---x---+
         _ _ | _ _ _ | _ _
        |    |p      |    |
        |    O       O    | City
        |                 |
        +-----------------+
        """
        CityFactory(
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)), srid=settings.SRID)
            ),
        )
        if settings.TREKKING_TOPOLOGY_ENABLED:
            p = PathFactory(
                geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5))
            )
            signage = SignageFactory.create(paths=[(p, 0.5, 0.5)])
        else:
            signage = SignageFactory.create(geom=Point(1, 1.5, srid=settings.SRID))
        self.assertEqual(len(signage.cities), 0)

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_city_with_topo_3(self):
        """
             +-------+
         _ _ | _ _ _ | _ _
        |    |p      |    |
        |    O       X S  | City
        |                 |
        +-----------------+
        """
        CityFactory(
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)), srid=settings.SRID)
            ),
        )
        if settings.TREKKING_TOPOLOGY_ENABLED:
            p = PathFactory(
                geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5))
            )
            signage = SignageFactory.create(paths=[(p, 1, 1)])
        else:
            signage = SignageFactory.create(geom=Point(1.5, 0.5, srid=settings.SRID))
        self.assertEqual(len(signage.cities), 1)

    def test_city_with_topo_on_loop(self):
        """
        +-----------------+
        |            S    |
        |    +-------x    |
        |    |       |    | City
        |    |p      |    |
        |    O-------+    |
        |                 |
        +-----------------+
        """
        CityFactory(
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)), srid=settings.SRID)
            ),
        )
        if settings.TREKKING_TOPOLOGY_ENABLED:
            p = PathFactory(
                geom=LineString(
                    (0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)
                )
            )
            signage = SignageFactory.create(paths=[(p, 0.5, 0.5)])
        else:
            signage = SignageFactory.create(geom=Point(1.5, 1.5, srid=settings.SRID))
        self.assertEqual(len(signage.cities), 1)

    def test_city_with_topo_on_loop_2(self):
        """
                     S
             +-------x
         _ _ | _ _ _ | _ _
        |    |p      |    |
        |    O-------+    | City
        |                 |
        +-----------------+
        """
        CityFactory(
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)), srid=settings.SRID)
            ),
        )
        if settings.TREKKING_TOPOLOGY_ENABLED:
            p = PathFactory(
                geom=LineString(
                    (0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)
                )
            )
            signage = SignageFactory.create(paths=[(p, 0.5, 0.5)])
        else:
            signage = SignageFactory.create(geom=Point(1.5, 1.5, srid=settings.SRID))
        self.assertEqual(len(signage.cities), 0)

    def test_city_with_topo_on_loop_3(self):
        """

             +-------+
         _ _ | _ _ _ | _ _
        |    |p      |    |
        |    O-------x S  | City
        |                 |
        +-----------------+
        """
        CityFactory(
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)), srid=settings.SRID)
            ),
        )
        if settings.TREKKING_TOPOLOGY_ENABLED:
            p = PathFactory(
                geom=LineString(
                    (0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)
                )
            )
            signage = SignageFactory.create(paths=[(p, 0.75, 0.75)])
        else:
            signage = SignageFactory.create(geom=Point(1.5, 0.5, srid=settings.SRID))
        self.assertEqual(len(signage.cities), 1)

    def test_couches_sig_link(self):
        """
        +-----------------+    -
        |                 |ra2  |
        |    +-------+    |     |
        | _ _|  _ _ _|_ _ |      - C
        |    |p      |    |     |
        |    O       O    |     |
        |                 |ra1  |
        +-----------------+    -
        """
        # Fake restricted areas
        RestrictedAreaFactory.create(
            geom=MultiPolygon(Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0))))
        )
        RestrictedAreaFactory.create(
            geom=MultiPolygon(Polygon(((0, 1), (2, 1), (2, 2), (0, 2), (0, 1))))
        )

        # Fake city
        CityFactory(
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)), srid=settings.SRID)
            ),
        )

        # Fake paths in these areas
        p = PathFactory(geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5)))

        self.assertEqual(len(p.areas), 2)
        self.assertEqual(len(p.cities), 1)

    def test_couches_sig_link_path_loop(self):
        """
        +-----------------+    -
        |                 |ra2  |
        |    +-------+    |     |
        | _ _|  _ _ _|_ _ |      - C
        |    |p      |    |     |
        |    O-------+    |     |
        |                 |ra1  |
        +-----------------+    -
        """
        # Fake restricted areas
        RestrictedAreaFactory.create(
            geom=MultiPolygon(Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0))))
        )
        RestrictedAreaFactory.create(
            geom=MultiPolygon(Polygon(((0, 1), (2, 1), (2, 2), (0, 2), (0, 1))))
        )

        # Fake city
        CityFactory(
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)), srid=settings.SRID)
            ),
        )

        # Fake paths in these areas
        p = PathFactory(
            geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5))
        )

        self.assertEqual(len(p.areas), 2)
        self.assertEqual(len(p.cities), 1)


class CityTestCase(TestCase):
    def test_city_str(self):
        """City __str__ method should return its name."""
        city = CityFactory()
        self.assertEqual(str(city), city.name)

    def test_city_last_updated_without_data(self):
        self.assertIsNone(City.latest_updated())

    def test_city_last_updated_with_data(self):
        city = CityFactory()
        self.assertIsNotNone(City.latest_updated())
        self.assertEqual(City.latest_updated(), city.date_update)


class DistrictTestCase(TestCase):
    def test_district_str(self):
        """District __str__ method should return its name."""
        district = DistrictFactory()
        self.assertEqual(str(district), district.name)

    def test_district_last_updated_without_data(self):
        self.assertIsNone(District.latest_updated())

    def test_district_last_updated_with_data(self):
        district = DistrictFactory()
        self.assertIsNotNone(District.latest_updated())
        self.assertEqual(District.latest_updated(), district.date_update)


class RestrictedAreaTestCase(TestCase):
    def test_restricted_area_str(self):
        """RestrictedArea __str__ method should return its type and its name."""
        restricted_area = RestrictedAreaFactory()
        self.assertEqual(
            str(restricted_area),
            f"{restricted_area.area_type} - {restricted_area.name}",
        )

    def test_restricted_area_last_updated_without_data(self):
        self.assertIsNone(RestrictedArea.latest_updated())

    def test_restricted_area_last_updated_with_data(self):
        restricted_area = RestrictedAreaFactory()
        self.assertIsNotNone(RestrictedArea.latest_updated())
        self.assertEqual(RestrictedArea.latest_updated(), restricted_area.date_update)

    def test_latest_updated_when_no_data_at_all(self):
        self.assertIsNone(RestrictedArea.latest_updated())

    def test_latest_updated_is_different_by_type(self):
        type_without_data = RestrictedAreaTypeFactory()
        type_with_data = RestrictedAreaTypeFactory()
        type_with_data_2 = RestrictedAreaTypeFactory()
        RestrictedAreaFactory.create_batch(5, area_type=type_with_data)
        RestrictedAreaFactory.create_batch(5, area_type=type_with_data_2)

        self.assertIsNone(RestrictedArea.latest_updated(type_without_data.pk))
        self.assertEqual(
            RestrictedArea.latest_updated(type_with_data.pk),
            type_with_data.restrictedarea_set.only("date_update")
            .latest("date_update")
            .date_update,
        )
        self.assertEqual(
            RestrictedArea.latest_updated(type_with_data_2.pk),
            type_with_data_2.restrictedarea_set.only("date_update")
            .latest("date_update")
            .date_update,
        )


class VigilanceAreaTypeTestCase(TestCase):
    def test_vigilance_area_type_str(self):
        vat = VigilanceAreaTypeFactory(name="Warning Type")
        self.assertEqual(str(vat), "Warning Type")


class VigilanceAreaModelTest(TestCase):
    def test_vigilance_area_str(self):
        va = VigilanceAreaFactory(name="My Vigilance Area")
        self.assertEqual(str(va), "My Vigilance Area")

    def test_clean_start_date_after_end_date(self):
        today = timezone_today()
        va = VigilanceAreaFactory.build(
            start_date=today,
            end_date=today - datetime.timedelta(days=1),
        )
        with self.assertRaises(ValidationError) as cm:
            va.clean()
        self.assertIn("start_date", cm.exception.error_dict)

    def test_clean_valid_dates(self):
        today = timezone_today()
        va = VigilanceAreaFactory.build(
            start_date=today,
            end_date=today + datetime.timedelta(days=5),
        )
        va.clean()

    def test_active_days_and_months_labels(self):
        va = VigilanceAreaFactory(active_days=[0, 6], active_months=[1, 12])
        self.assertEqual(len(va.active_days_labels), 2)
        self.assertEqual(len(va.active_months_labels), 2)

    def test_verbose_name_properties(self):
        va = VigilanceAreaFactory()
        self.assertEqual(str(va.period_active_verbose_name), "Period active")
        self.assertEqual(str(va.active_today_verbose_name), "Active today")

    def test_period_resume(self):
        today = timezone_today()
        va_no_end = VigilanceAreaFactory(
            start_date=today,
            end_date=None,
            active_days=[0],
            active_months=[1],
        )
        self.assertIn(str(today), va_no_end.period_resume)

        va_with_end = VigilanceAreaFactory(
            start_date=today,
            end_date=today + datetime.timedelta(days=10),
            active_days=[],
            active_months=[],
        )
        self.assertIn(str(today), va_with_end.period_resume)
        self.assertIn(
            str(today + datetime.timedelta(days=10)), va_with_end.period_resume
        )


class VigilanceAreaManagerTest(TestCase):
    def setUp(self):
        self.today = timezone_today()
        self.yesterday = self.today - datetime.timedelta(days=1)
        self.tomorrow = self.today + datetime.timedelta(days=1)
        self.last_week = self.today - datetime.timedelta(days=7)

    def test_manager_period_active_and_finished(self):
        va_active = VigilanceAreaFactory(start_date=self.yesterday, end_date=None)
        va_active_until_tomorrow = VigilanceAreaFactory(
            start_date=self.yesterday, end_date=self.tomorrow
        )
        va_finished = VigilanceAreaFactory(
            start_date=self.last_week, end_date=self.yesterday
        )
        va_future = VigilanceAreaFactory(start_date=self.tomorrow, end_date=None)

        active_qs = VigilanceArea.objects.active()
        self.assertIn(va_active, active_qs)
        self.assertIn(va_active_until_tomorrow, active_qs)
        self.assertNotIn(va_finished, active_qs)
        self.assertNotIn(va_future, active_qs)

        finished_qs = VigilanceArea.objects.finished()
        self.assertIn(va_finished, finished_qs)
        self.assertNotIn(va_active, finished_qs)

    def test_manager_active_today(self):
        weekday = self.today.weekday()
        other_weekday = (weekday + 1) % 7
        month = self.today.month
        other_month = (month % 12) + 1

        va_today = VigilanceAreaFactory(
            start_date=self.yesterday,
            end_date=None,
            active_days=[weekday],
            active_months=[month],
        )
        va_wrong_day = VigilanceAreaFactory(
            start_date=self.yesterday,
            end_date=None,
            active_days=[other_weekday],
            active_months=[month],
        )
        va_wrong_month = VigilanceAreaFactory(
            start_date=self.yesterday,
            end_date=None,
            active_days=[weekday],
            active_months=[other_month],
        )

        qs = VigilanceArea.objects.all()
        self.assertTrue(qs.get(pk=va_today.pk).active_today)
        self.assertFalse(qs.get(pk=va_wrong_day.pk).active_today)
        self.assertFalse(qs.get(pk=va_wrong_month.pk).active_today)

    def test_active_by_date(self):
        va = VigilanceAreaFactory(start_date=self.yesterday, end_date=None)
        qs = VigilanceArea.objects.active_by_date()
        self.assertIn(va, qs)
