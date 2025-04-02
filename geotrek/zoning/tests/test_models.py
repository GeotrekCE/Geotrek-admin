from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import LineString, MultiPolygon, Point, Polygon
from django.test import TestCase

from geotrek.core.tests.factories import PathFactory
from geotrek.signage.tests.factories import SignageFactory
from geotrek.zoning.models import City
from geotrek.zoning.tests.factories import (
    CityFactory,
    DistrictFactory,
    RestrictedAreaFactory,
    RestrictedAreaTypeFactory,
)


class PathUpdateTest(TestCase):
    def test_path_touching_land_layer(self):
        p1 = PathFactory.create(geom=LineString((3, 3), (4, 4), srid=settings.SRID))
        City.objects.create(
            code="005177",
            name="Trifouillis-les-oies",
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)), srid=settings.SRID)
            ),
        )
        p1.geom = LineString((2, 2), (4, 4), srid=settings.SRID)
        p1.save()


class ZoningLayersUpdateTest(TestCase):
    def test_paths_link(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (1, 1)))
        p2 = PathFactory.create(geom=LineString((1, 1), (3, 3)))
        p3 = PathFactory.create(geom=LineString((3, 3), (4, 4)))
        p4 = PathFactory.create(geom=LineString((4, 1), (6, 2), (4, 3)))

        c1 = City.objects.create(
            code="005177",
            name="Trifouillis-les-oies",
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 4), (0, 4), (0, 0)), srid=settings.SRID)
            ),
        )
        City.objects.create(
            code="005179",
            name="Trifouillis-les-poules",
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
        p1.save()
        c = City(
            code="005178",
            name="Trifouillis-les-marmottes",
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)), srid=settings.SRID)
            ),
        )
        c.save()
        # Create a path after city to the the another trigger
        p2 = PathFactory(geom=LineString((1.5, 2), (1.5, 1)))
        p2.save()
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
        c = City(
            code="005178",
            name="Trifouillis-les-marmottes",
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)), srid=settings.SRID)
            ),
        )
        c.save()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            p = PathFactory(
                geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5))
            )
            p.save()
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
        c = City(
            code="005178",
            name="Trifouillis-les-marmottes",
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)), srid=settings.SRID)
            ),
        )
        c.save()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            p = PathFactory(
                geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5))
            )
            p.save()
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
        c = City(
            code="005178",
            name="Trifouillis-les-marmottes",
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)), srid=settings.SRID)
            ),
        )
        c.save()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            p = PathFactory(
                geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5))
            )
            p.save()
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
        c = City(
            code="005178",
            name="Trifouillis-les-marmottes",
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)), srid=settings.SRID)
            ),
        )
        c.save()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            p = PathFactory(
                geom=LineString(
                    (0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)
                )
            )
            p.save()
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
        c = City(
            code="005178",
            name="Trifouillis-les-marmottes",
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)), srid=settings.SRID)
            ),
        )
        c.save()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            p = PathFactory(
                geom=LineString(
                    (0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)
                )
            )
            p.save()
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
        c = City(
            code="005178",
            name="Trifouillis-les-marmottes",
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 1), (0, 1), (0, 0)), srid=settings.SRID)
            ),
        )
        c.save()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            p = PathFactory(
                geom=LineString(
                    (0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)
                )
            )
            p.save()
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
        c = City(
            code="005178",
            name="Trifouillis-les-marmottes",
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)), srid=settings.SRID)
            ),
        )
        c.save()

        # Fake paths in these areas
        p = PathFactory(geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5)))
        p.save()

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
        c = City(
            code="005178",
            name="Trifouillis-les-marmottes",
            geom=MultiPolygon(
                Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)), srid=settings.SRID)
            ),
        )
        c.save()

        # Fake paths in these areas
        p = PathFactory(
            geom=LineString((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5))
        )
        p.save()

        self.assertEqual(len(p.areas), 2)
        self.assertEqual(len(p.cities), 1)


class ZoningModelsTest(TestCase):
    def test_city(self):
        city = CityFactory.create(
            name="Are",
            code="09000",
            geom=MultiPolygon(
                Polygon(
                    ((200, 0), (300, 0), (300, 100), (200, 100), (200, 0)),
                    srid=settings.SRID,
                )
            ),
        )
        self.assertEqual(str(city), "Are")

    def test_district(self):
        district = DistrictFactory.create(
            name="Lil",
            geom=MultiPolygon(
                Polygon(
                    ((201, 0), (300, 0), (300, 100), (200, 100), (201, 0)),
                    srid=settings.SRID,
                )
            ),
        )
        self.assertEqual(str(district), "Lil")

    def test_restricted_area(self):
        area_type = RestrictedAreaTypeFactory.create(name="Test")
        restricted_area = RestrictedAreaFactory.create(
            area_type=area_type,
            name="Tel",
            geom=MultiPolygon(
                Polygon(
                    ((201, 0), (300, 0), (300, 100), (200, 100), (201, 0)),
                    srid=settings.SRID,
                )
            ),
        )
        self.assertEqual(str(restricted_area), "Test - Tel")
