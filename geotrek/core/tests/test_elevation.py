from django.conf import settings
from django.test import TestCase
from django.db import connections, DEFAULT_DB_ALIAS
from django.contrib.gis.geos import MultiLineString, LineString

from geotrek.core.models import Path
from geotrek.core.factories import TopologyFactory
from geotrek.core.helpers import AltimetryHelper


class ElevationTest(TestCase):

    def setUp(self):
        # Create a simple fake DEM
        conn = connections[DEFAULT_DB_ALIAS]
        cur = conn.cursor()
        cur.execute('CREATE TABLE mnt (rid serial primary key, rast raster)')
        cur.execute('INSERT INTO mnt (rast) VALUES (ST_MakeEmptyRaster(100, 125, 0, 125, 25, -25, 0, 0, %s))', [settings.SRID])
        cur.execute('UPDATE mnt SET rast = ST_AddBand(rast, \'16BSI\')')
        demvalues = [[0, 0, 3, 5], [2, 2, 10, 15], [5, 15, 20, 25], [20, 25, 30, 35], [30, 35, 40, 45]]
        for y in range(0, 5):
            for x in range(0, 4):
                cur.execute('UPDATE mnt SET rast = ST_SetValue(rast, %s, %s, %s::float)', [x + 1, y + 1, demvalues[y][x]])

        self.path = Path.objects.create(geom=LineString((78, 117), (3, 17)))

    def test_elevation_path(self):
        self.assertEqual(self.path.ascent, 20)
        self.assertEqual(self.path.descent, -3)
        self.assertEqual(self.path.min_elevation, 4)
        self.assertEqual(self.path.max_elevation, 22)
        self.assertEqual(len(self.path.geom_3d.coords), 6)

    def test_elevation_profile(self):
        profile = self.path.get_elevation_profile()
        self.assertEqual(len(profile), 6)
        self.assertEqual(profile[0][0], 0.0)
        self.assertEqual(profile[-1][0], 125.0)
        self.assertEqual(profile[0][3], 5.0)
        self.assertEqual(profile[1][3], 7.0)
        self.assertEqual(profile[2][3], 4.0)
        self.assertEqual(profile[3][3], 9.0)
        self.assertEqual(profile[4][3], 14.0)
        self.assertEqual(profile[5][3], 22.0)

    def test_elevation_topology_line(self):
        topo = TopologyFactory.create(no_path=True)
        topo.add_path(self.path, start=0.2, end=0.8)
        topo.save()

        self.assertEqual(topo.ascent, 5)
        self.assertEqual(topo.descent, -2)
        self.assertEqual(topo.min_elevation, 5)
        self.assertEqual(topo.max_elevation, 10)
        self.assertEqual(len(topo.geom_3d.coords), 4)

    def test_elevation_topology_point(self):
        topo = TopologyFactory.create(no_path=True)
        topo.add_path(self.path, start=0.6, end=0.6)
        topo.save()
        self.assertEqual(topo.geom_3d.coords[2], 15)
        self.assertEqual(topo.ascent, 0)
        self.assertEqual(topo.descent, 0)
        self.assertEqual(topo.min_elevation, 15)
        self.assertEqual(topo.max_elevation, 15)

    def test_elevation_topology_point_offset(self):
        topo = TopologyFactory.create(no_path=True,offset=1)
        topo.add_path(self.path, start=0.5, end=0.5)
        topo.save()
        self.assertEqual(topo.geom_3d.coords[2], 15)
        self.assertEqual(topo.ascent, 0)
        self.assertEqual(topo.descent, 0)
        self.assertEqual(topo.min_elevation, 15)
        self.assertEqual(topo.max_elevation, 15)


class ElevationProfileTest(TestCase):
    def test_elevation_profile_wrong_geom(self):
        geom = MultiLineString(LineString((1.5, 2.5, 8), (2.5, 2.5, 10)),
                               LineString((2.5, 2.5, 6), (2.5, 0, 7)),
                               srid=settings.SRID)

        profile = AltimetryHelper.elevation_profile(geom)
        self.assertEqual(len(profile), 4)

    def test_elevation_svg_output(self):
        geom = LineString((1.5, 2.5, 8), (2.5, 2.5, 10),
                          srid=settings.SRID)
        profile = AltimetryHelper.elevation_profile(geom)
        svg = AltimetryHelper.profile_svg(profile)
        self.assertIn('Generated with pygal', svg)
        self.assertIn(settings.ALTIMETRIC_PROFILE_BACKGROUND, svg)
        self.assertIn(settings.ALTIMETRIC_PROFILE_COLOR, svg)


class ElevationAreaTest(TestCase):
    def setUp(self):
        self.geom = LineString((0, 0), (1000, 0), srid=settings.SRID)
        self.area = AltimetryHelper.elevation_area(self.geom)

    def test_area_has_nice_ratio_if_horizontal(self):
        self.assertEqual(self.area['extent']['width'], 1000 + 2*100)
        self.assertEqual(self.area['extent']['height'], 732.6007326007326)

    def test_area_has_nice_ratio_if_vertical(self):
        geom = LineString((0, 0), (0, 1000), srid=settings.SRID)
        area = AltimetryHelper.elevation_area(geom)
        self.assertEqual(area['extent']['width'], 732.6007326007326)
        self.assertEqual(area['extent']['height'], 1000 + 2*100)

    def test_area_has_nice_ratio_if_square_enough(self):
        geom = LineString((0, 0), (1000, 1000), srid=settings.SRID)
        area = AltimetryHelper.elevation_area(geom)
        self.assertEqual(area['extent']['width'], 1000 + 2*100)
        self.assertEqual(area['extent']['height'], 1000 + 2*100)

    def test_area_provides_altitudes_as_matrix(self):
        self.assertEqual(len(area['altitudes']), 52)
        self.assertEqual(len(area['altitudes'][0]), 14)
