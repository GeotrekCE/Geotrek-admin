from unittest import SkipTest, skipIf

from django.conf import settings
from django.contrib.gis.geos import LineString, MultiLineString, Point
from django.db import connection
from django.test import TestCase

from geotrek.altimetry.helpers import AltimetryHelper
from geotrek.core.models import Path, Topology
from geotrek.core.tests.factories import TopologyFactory


class ElevationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a simple fake DEM
        with connection.cursor() as cur:
            cur.execute(
                "INSERT INTO altimetry_dem (rast) VALUES (ST_MakeEmptyRaster(100, 125, 0, 125, 25, -25, 0, 0, %s))",
                [settings.SRID],
            )
            cur.execute("UPDATE altimetry_dem SET rast = ST_AddBand(rast, '16BSI')")
            demvalues = [
                [0, 0, 3, 5],
                [2, 2, 10, 15],
                [5, 15, 20, 25],
                [20, 25, 30, 35],
                [30, 35, 40, 45],
            ]
            for y in range(0, 5):
                for x in range(0, 4):
                    cur.execute(
                        "UPDATE altimetry_dem SET rast = ST_SetValue(rast, %s, %s, %s::float)",
                        [x + 1, y + 1, demvalues[y][x]],
                    )
            if settings.TREKKING_TOPOLOGY_ENABLED:
                cls.path = Path.objects.create(geom=LineString((78, 117), (3, 17)))

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_elevation_path(self):
        self.assertEqual(self.path.ascent, 16)
        self.assertEqual(self.path.descent, 0)
        self.assertEqual(self.path.min_elevation, 6)
        self.assertEqual(self.path.max_elevation, 22)
        self.assertEqual(len(self.path.geom_3d.coords), 7)

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_elevation_profile(self):
        profile = self.path.get_elevation_profile()
        self.assertAlmostEqual(len(profile), 7)
        self.assertAlmostEqual(profile[0][0], 0.0)
        self.assertAlmostEqual(profile[-1][0], 125.0)
        self.assertAlmostEqual(profile[0][3], 6.0)
        self.assertAlmostEqual(profile[1][3], 8.0)
        self.assertAlmostEqual(profile[2][3], 10.0)
        self.assertAlmostEqual(profile[3][3], 13.0)
        self.assertAlmostEqual(profile[4][3], 18.0)
        self.assertAlmostEqual(profile[5][3], 20.0)
        self.assertAlmostEqual(profile[6][3], 22.0)

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_elevation_limits(self):
        limits = self.path.get_elevation_limits()
        self.assertEqual(limits[0], 1106)
        self.assertEqual(limits[1], -94)

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_elevation_topology_line(self):
        topo = TopologyFactory.create(paths=[(self.path, 0.2, 0.8)])
        topo.save()
        topo.get_elevation_profile()
        self.assertEqual(topo.ascent, 7)
        self.assertEqual(topo.descent, 0)
        self.assertEqual(topo.min_elevation, 10)
        self.assertEqual(topo.max_elevation, 17)
        self.assertEqual(len(topo.geom_3d.coords), 5)

    @skipIf(
        settings.TREKKING_TOPOLOGY_ENABLED, "Test without dynamic segmentation only"
    )
    def test_elevation_topology_line_nds(self):
        """
        No reason for this changements
        """
        topo = TopologyFactory.create(geom="SRID=2154;LINESTRING(63 97, 18 37)")
        topo.get_elevation_profile()
        self.assertEqual(topo.ascent, 5)
        self.assertEqual(topo.descent, 0)
        self.assertEqual(topo.min_elevation, 12)
        self.assertEqual(topo.max_elevation, 17)
        self.assertEqual(len(topo.geom_3d.coords), 5)

    @skipIf(
        settings.TREKKING_TOPOLOGY_ENABLED, "Test without dynamic segmentation only"
    )
    def test_elevation_topology_point(self):
        topo = TopologyFactory.create(geom="SRID=2154;POINT(33 57)")
        self.assertEqual(topo.geom_3d.coords[2], 15)
        self.assertEqual(topo.ascent, 0)
        self.assertEqual(topo.descent, 0)
        self.assertEqual(topo.min_elevation, 15)
        self.assertEqual(topo.max_elevation, 15)

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_elevation_topology_point_offset(self):
        topo = TopologyFactory.create(paths=[(self.path, 0.5, 0.5)], offset=1)
        self.assertEqual(topo.geom_3d.coords[2], 15)
        self.assertEqual(topo.ascent, 0)
        self.assertEqual(topo.descent, 0)
        self.assertEqual(topo.min_elevation, 15)
        self.assertEqual(topo.max_elevation, 15)

    def test_elevation_topology_outside_dem(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            outside_path = Path.objects.create(geom=LineString((200, 200), (300, 300)))
            topo = TopologyFactory.create(paths=[(outside_path, 0.5, 0.5)])
        else:
            topo = TopologyFactory.create(geom="SRID=2154;POINT(250 250)")
        self.assertEqual(topo.geom_3d.coords[2], 0)
        self.assertEqual(topo.ascent, 0)
        self.assertEqual(topo.descent, 0)
        self.assertEqual(topo.min_elevation, 0)
        self.assertEqual(topo.max_elevation, 0)


class ElevationProfileTest(TestCase):
    def test_elevation_profile_multilinestring(self):
        geom = MultiLineString(
            LineString((1.5, 2.5, 8), (2.5, 2.5, 10)),
            LineString((2.5, 2.5, 6), (2.5, 0, 7)),
            srid=settings.SRID,
        )

        profile = AltimetryHelper.elevation_profile(geom)
        self.assertEqual(len(profile), 4)

    def test_elevation_profile_point(self):
        geom = Point(1.5, 2.5, 8, srid=settings.SRID)

        profile = AltimetryHelper.elevation_profile(geom)
        self.assertEqual(profile, [[0, 1.5, 2.5, 8.0]])

    def test_elevation_svg_output(self):
        geom = LineString((1.5, 2.5, 8), (2.5, 2.5, 10), srid=settings.SRID)
        profile = AltimetryHelper.elevation_profile(geom)
        svg = AltimetryHelper.profile_svg(profile, "en")
        self.assertIn("Generated with pygal".encode(), svg)
        self.assertIn(settings.ALTIMETRIC_PROFILE_BACKGROUND.encode(), svg)
        self.assertIn(settings.ALTIMETRIC_PROFILE_COLOR.encode(), svg)

    def test_elevation_altimetry_limits(self):
        geom = LineString((1.5, 2.5, 8), (2.5, 2.5, 10), srid=settings.SRID)
        profile = AltimetryHelper.elevation_profile(geom)
        limits = AltimetryHelper.altimetry_limits(profile)
        self.assertEqual(limits[0], 1108)
        self.assertEqual(limits[1], -92)


def fill_raster():
    with connection.cursor() as cur:
        cur.execute(
            "INSERT INTO altimetry_dem (rast) VALUES (ST_MakeEmptyRaster(100, 125, 0, 125, 25, -25, 0, 0, %s))",
            [settings.SRID],
        )
        cur.execute("UPDATE altimetry_dem SET rast = ST_AddBand(rast, '16BSI')")
        demvalues = [
            [0, 0, 3, 5],
            [2, 2, 10, 15],
            [5, 15, 20, 25],
            [20, 25, 30, 35],
            [30, 35, 40, 45],
        ]
        for y in range(0, 5):
            for x in range(0, 4):
                cur.execute(
                    "UPDATE altimetry_dem SET rast = ST_SetValue(rast, %s, %s, %s::float)",
                    [x + 1, y + 1, demvalues[y][x]],
                )


class ElevationAreaTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_raster()
        cls.geom = LineString((100, 370), (1100, 370), srid=settings.SRID)
        cls.area = AltimetryHelper.elevation_area(cls.geom)

    def test_area_has_nice_ratio_if_horizontal(self):
        self.assertEqual(self.area["size"]["x"], 1300.0)
        self.assertEqual(self.area["size"]["y"], 800.0)

    def test_area_provides_altitudes_as_matrix(self):
        self.assertEqual(len(self.area["altitudes"]), 33)
        self.assertEqual(len(self.area["altitudes"][0]), 53)
        self.assertEqual(len(self.area["altitudes"][-1]), 53)

    def test_area_provides_resolution(self):
        self.assertEqual(self.area["resolution"]["x"], 53)
        self.assertEqual(self.area["resolution"]["y"], 33)

    def test_resolution_step_depends_on_geometry_size(self):
        self.assertEqual(self.area["resolution"]["step"], 25)
        geom = LineString((100, 370), (100100, 370), srid=settings.SRID)
        area = AltimetryHelper.elevation_area(geom)
        self.assertEqual(area["resolution"]["step"], 866)

    def test_area_provides_center_as_latlng(self):
        self.assertAlmostEqual(self.area["center"]["lng"], -1.3594758650394245)
        self.assertAlmostEqual(self.area["center"]["lat"], -5.981351702397734)

    def test_area_provides_center_as_xy(self):
        self.assertEqual(self.area["center"]["x"], 600.0)
        self.assertEqual(self.area["center"]["y"], 369.0)

    def test_area_provides_extent_as_xy(self):
        extent = self.area["extent"]
        self.assertEqual(extent["northwest"]["x"], -50.0)
        self.assertEqual(extent["northwest"]["y"], 769.0)
        self.assertEqual(extent["southeast"]["x"], 1250.0)
        self.assertEqual(extent["southeast"]["y"], -31.0)

    def test_area_provides_extent_as_latlng(self):
        extent = self.area["extent"]
        self.assertAlmostEqual(extent["northeast"]["lat"], -5.9786368380250385)
        self.assertAlmostEqual(extent["northeast"]["lng"], -1.35556992351484)
        self.assertAlmostEqual(extent["southwest"]["lat"], -5.9840665893459875)
        self.assertAlmostEqual(extent["southwest"]["lng"], -1.3633815583740085)

    def test_area_provides_altitudes_extent(self):
        extent = self.area["extent"]
        self.assertEqual(extent["altitudes"]["max"], 45)
        self.assertEqual(extent["altitudes"]["min"], 0)


class ElevationOtherGeomAreaTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_raster()

    def test_area_small_geom(self):
        geom = LineString((10, 10), (10, 5), srid=settings.SRID)
        area = AltimetryHelper.elevation_area(geom)
        extent = area["extent"]
        self.assertEqual(extent["altitudes"]["max"], 30)
        self.assertEqual(extent["altitudes"]["min"], 30)

    def test_area_has_nice_ratio_if_vertical(self):
        geom = LineString((0, 0), (0, 1000), srid=settings.SRID)
        area = AltimetryHelper.elevation_area(geom)
        self.assertEqual(area["size"]["x"], 800.0)
        self.assertEqual(area["size"]["y"], 1300.0)

    def test_area_has_nice_ratio_if_square_enough(self):
        geom = LineString((0, 0), (1000, 1000), srid=settings.SRID)
        area = AltimetryHelper.elevation_area(geom)
        self.assertEqual(area["size"]["x"], 1300.0)
        self.assertEqual(area["size"]["y"], 1300.0)


def fill_raster_order():
    with connection.cursor() as cur:
        cur.execute(
            "INSERT INTO altimetry_dem (rast) VALUES (ST_MakeEmptyRaster(250, 250, 0, 250, 25, -25, 0, 0, %s))",
            [settings.SRID],
        )
        cur.execute("UPDATE altimetry_dem SET rast = ST_AddBand(rast, '16BSI')")
        demvalues = []
        for x in range(0, 10):
            demvalues.append(list(range(x * 2, x * 2 + 10)))

        for y in range(0, 10):
            for x in range(0, 10):
                cur.execute(
                    "UPDATE altimetry_dem SET rast = ST_SetValue(rast, %s, %s, %s::float)",
                    [x + 1, y + 1, demvalues[y][x]],
                )


class ElevationRightOrderAreaTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        fill_raster_order()

    def test_area_order_lines_columns(self):
        """
        We check that the order is always the same not depending on the database.
        Firstly we iterate on lines then columns. And it should be always the same order.
        """
        geom = LineString((125, 240), (125, 50), srid=settings.SRID)
        area_1 = AltimetryHelper.elevation_area(geom)

        self.assertEqual(
            area_1["altitudes"],
            [
                [18, 19, 20, 21, 22, 23, 24],
                [16, 17, 18, 19, 20, 21, 22],
                [14, 15, 16, 17, 18, 19, 20],
                [12, 13, 14, 15, 16, 17, 18],
                [10, 11, 12, 13, 14, 15, 16],
                [8, 9, 10, 11, 12, 13, 14],
                [6, 7, 8, 9, 10, 11, 12],
                [4, 5, 6, 7, 8, 9, 10],
                [2, 3, 4, 5, 6, 7, 8],
                [0, 1, 2, 3, 4, 5, 6],
            ],
        )

        geom = LineString((240, 125), (50, 125), srid=settings.SRID)
        area_2 = AltimetryHelper.elevation_area(geom)
        self.assertEqual(
            area_2["altitudes"],
            [
                [12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
                [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
                [8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
                [6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                [4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
                [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            ],
        )


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, "Test without dynamic segmentation only")
class LengthTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a simple fake DEM
        with connection.cursor() as cur:
            cur.execute(
                "INSERT INTO altimetry_dem (rast) VALUES (ST_MakeEmptyRaster(100, 125, 0, 125, 25, -25, 0, 0, %s))",
                [settings.SRID],
            )
            cur.execute("UPDATE altimetry_dem SET rast = ST_AddBand(rast, '16BSI')")
            demvalues = [
                [0, 0, 3, 5],
                [2, 2, 10, 15],
                [5, 15, 20, 25],
                [20, 25, 30, 35],
                [30, 35, 40, 45],
            ]
            for y in range(0, 5):
                for x in range(0, 4):
                    cur.execute(
                        "UPDATE altimetry_dem SET rast = ST_SetValue(rast, %s, %s, %s::float)",
                        [x + 1, y + 1, demvalues[y][x]],
                    )
            cls.path = Path.objects.create(
                geom=LineString((1, 101), (81, 101), (81, 99))
            )

    def test_2dlength_is_preserved(self):
        self.assertEqual(self.path.geom_3d.length, self.path.geom.length)

    def test_3dlength(self):
        # before smoothing: (1 101 0, 21 101 0, 41 101 0, 61 101 3, 81 101 5, 81 99 15)
        # after smoothing:  (1 101 0, 21 101 0, 41 101 0, 61 101 1, 81 101 3, 81 99  9)
        # length: 20 + 20 + (20 ** 2 + 1) ** .5 + (20 ** 2 + 2 ** 2) ** .5 + (2 ** 2 + 6 ** 2) ** .5
        self.assertEqual(round(self.path.length, 9), 83.127128724)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class SamplingTestPath(TestCase):
    model = Path
    step = settings.ALTIMETRIC_PROFILE_PRECISION

    @classmethod
    def setUpTestData(cls):
        if cls.model is None:
            SkipTest(reason="No model")
        # Create a fake empty DEM to prevent trigger optimisation to skip sampling
        with connection.cursor() as cur:
            cur.execute(
                "INSERT INTO altimetry_dem (rast) VALUES (ST_AddBand(ST_MakeEmptyRaster(100, 100, 0, 100, 25, -25, 0, 0, %s), '16BSI'))",
                [settings.SRID],
            )

    def test_0_first(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, 0), (0, 1)))
        self.assertEqual(len(path.geom_3d.coords), 3)

    def test_0_last(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, 1), (0, 1)))
        self.assertEqual(len(path.geom_3d.coords), 3)

    def test_1(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, 1)))
        self.assertEqual(len(path.geom_3d.coords), 2)

    def test_24(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, self.step - 1)))
        self.assertEqual(len(path.geom_3d.coords), 2)

    def test_25(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, self.step)))
        self.assertEqual(len(path.geom_3d.coords), 3)

    def test_26(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, self.step + 1)))
        self.assertEqual(len(path.geom_3d.coords), 3)

    def test_49(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step * 2 - 1))
        )
        self.assertEqual(len(path.geom_3d.coords), 3)

    def test_50(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, self.step * 2)))
        self.assertEqual(len(path.geom_3d.coords), 4)

    def test_51(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step * 2 + 1))
        )
        self.assertEqual(len(path.geom_3d.coords), 4)

    def test_1m(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, 1), (1, 1)))
        self.assertEqual(len(path.geom_3d.coords), 3)

    def test_24m(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step - 1), (0, self.step * 2 - 2))
        )
        self.assertEqual(len(path.geom_3d.coords), 3)

    def test_25m(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step), (0, self.step * 2))
        )
        self.assertEqual(len(path.geom_3d.coords), 5)

    def test_26m(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step + 1), (0, self.step * 2 + 2))
        )
        self.assertEqual(len(path.geom_3d.coords), 5)

    def test_49m(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step * 2 - 1), (0, self.step * 4 - 2))
        )
        self.assertEqual(len(path.geom_3d.coords), 5)

    def test_50m(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step * 2), (0, self.step * 4))
        )
        self.assertEqual(len(path.geom_3d.coords), 7)

    def test_51m(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step * 2 + 1), (0, self.step * 4 + 2))
        )
        self.assertEqual(len(path.geom_3d.coords), 7)


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, "Test without dynamic segmentation only")
class SamplingTestTopology(TestCase):
    model = Topology
    step = settings.ALTIMETRIC_PROFILE_PRECISION

    @classmethod
    def setUpTestData(cls):
        if cls.model is None:
            SkipTest(reason="None")
        # Create a fake empty DEM to prevent trigger optimisation to skip sampling
        with connection.cursor() as cur:
            cur.execute(
                "INSERT INTO altimetry_dem (rast) VALUES (ST_MakeEmptyRaster(100, 125, 0, 125, 25, -25, 0, 0, %s))",
                [settings.SRID],
            )
            cur.execute("UPDATE altimetry_dem SET rast = ST_AddBand(rast, '16BSI')")

    def test_0_first(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, 0), (0, 1)))
        self.assertEqual(len(path.geom_3d.coords), 3)

    def test_0_last(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, 1), (0, 1)))
        self.assertEqual(len(path.geom_3d.coords), 3)

    def test_1(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, 1)))
        self.assertEqual(len(path.geom_3d.coords), 2)

    def test_24(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, self.step - 1)))
        self.assertEqual(len(path.geom_3d.coords), 2)

    def test_25(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, self.step)))
        self.assertEqual(len(path.geom_3d.coords), 3)

    def test_26(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, self.step + 1)))
        self.assertEqual(len(path.geom_3d.coords), 3)

    def test_49(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step * 2 - 1))
        )
        self.assertEqual(len(path.geom_3d.coords), 3)

    def test_50(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, self.step * 2)))
        self.assertEqual(len(path.geom_3d.coords), 4)

    def test_51(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step * 2 + 1))
        )
        self.assertEqual(len(path.geom_3d.coords), 4)

    def test_1m(self):
        path = self.model.objects.create(geom=LineString((0, 0), (0, 1), (1, 1)))
        self.assertEqual(len(path.geom_3d.coords), 3)

    def test_24m(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step - 1), (0, self.step * 2 - 2))
        )
        self.assertEqual(len(path.geom_3d.coords), 3)

    def test_25m(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step), (0, self.step * 2))
        )
        self.assertEqual(len(path.geom_3d.coords), 5)

    def test_26m(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step + 1), (0, self.step * 2 + 2))
        )
        self.assertEqual(len(path.geom_3d.coords), 5)

    def test_49m(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step * 2 - 1), (0, self.step * 4 - 2))
        )
        self.assertEqual(len(path.geom_3d.coords), 5)

    def test_50m(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step * 2), (0, self.step * 4))
        )
        self.assertEqual(len(path.geom_3d.coords), 7)

    def test_51m(self):
        path = self.model.objects.create(
            geom=LineString((0, 0), (0, self.step * 2 + 1), (0, self.step * 4 + 2))
        )
        self.assertEqual(len(path.geom_3d.coords), 7)
