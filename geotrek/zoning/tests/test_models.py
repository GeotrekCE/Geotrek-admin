from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import LineString, MultiPolygon, Point, Polygon
from django.test import TestCase

from geotrek.core.tests.factories import PathFactory
from geotrek.signage.tests.factories import SignageFactory
from geotrek.zoning.models import City, District, RestrictedArea
from geotrek.zoning.tests.factories import (
    CityFactory,
    DistrictFactory,
    RestrictedAreaFactory,
    RestrictedAreaTypeFactory,
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
