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
        self._fill_raster()
        self.geom = LineString((100, 370), (1100, 370), srid=settings.SRID)
        self.area = AltimetryHelper.elevation_area(self.geom)

    def _fill_raster(self):
        conn = connections[DEFAULT_DB_ALIAS]
        cur = conn.cursor()
        cur.execute('CREATE TABLE mnt (rid serial primary key, rast raster)')
        cur.execute('INSERT INTO mnt (rast) VALUES (ST_MakeEmptyRaster(100, 125, 0, 125, 25, -25, 0, 0, %s))', [settings.SRID])
        cur.execute('UPDATE mnt SET rast = ST_AddBand(rast, \'16BSI\')')
        demvalues = [[0, 0, 3, 5], [2, 2, 10, 15], [5, 15, 20, 25], [20, 25, 30, 35], [30, 35, 40, 45]]
        for y in range(0, 5):
            for x in range(0, 4):
                cur.execute('UPDATE mnt SET rast = ST_SetValue(rast, %s, %s, %s::float)', [x + 1, y + 1, demvalues[y][x]])

    def test_area_has_nice_ratio_if_horizontal(self):
        self.assertEqual(self.area['size']['x'], 1200.0)
        self.assertEqual(self.area['size']['y'], 725.0)

    def test_area_has_nice_ratio_if_vertical(self):
        geom = LineString((0, 0), (0, 1000), srid=settings.SRID)
        area = AltimetryHelper.elevation_area(geom)
        self.assertEqual(area['size']['x'], 725.0)
        self.assertEqual(area['size']['y'], 1200.0)

    def test_area_has_nice_ratio_if_square_enough(self):
        geom = LineString((0, 0), (1000, 1000), srid=settings.SRID)
        area = AltimetryHelper.elevation_area(geom)
        self.assertEqual(area['size']['x'], 1200.0)
        self.assertEqual(area['size']['y'], 1175.0)

    def test_area_provides_altitudes_as_matrix(self):
        self.assertEqual(len(self.area['altitudes']), 30)
        self.assertEqual(len(self.area['altitudes'][0]), 49)
        self.assertEqual(len(self.area['altitudes'][-1]), 49)

    def test_area_provides_resolution(self):
        self.assertEqual(self.area['resolution']['x'], 49)
        self.assertEqual(self.area['resolution']['y'], 30)

    def test_resolution_step_depends_on_geometry_size(self):
        self.assertEqual(self.area['resolution']['step'], 25)
        geom = LineString((100, 370), (100100, 370), srid=settings.SRID)
        area = AltimetryHelper.elevation_area(geom)
        self.assertEqual(area['resolution']['step'], 668)

    def test_area_provides_center_as_latlng(self):
        self.assertEqual(self.area['center']['lng'], -1.3594736317756084)
        self.assertEqual(self.area['center']['lat'], -5.981392181086671)

    def test_area_provides_center_as_xy(self):
        self.assertEqual(self.area['center']['x'], 600.0)
        self.assertEqual(self.area['center']['y'], 362.5)

    def test_area_provides_extent_as_xy(self):
        extent = self.area['extent']
        self.assertEqual(extent['northwest']['x'], 0)
        self.assertEqual(extent['northwest']['y'], 725.0)
        self.assertEqual(extent['southeast']['x'], 1200.0)
        self.assertEqual(extent['southeast']['y'], 0)

    def test_area_provides_extent_as_latlng(self):
        extent = self.area['extent']
        self.assertEqual(extent['northeast']['lat'], -5.978928071058993)
        self.assertEqual(extent['northeast']['lng'], -1.3558658459929058)
        self.assertEqual(extent['southwest']['lat'], -5.98385630920877)
        self.assertEqual(extent['southwest']['lng'], -1.3630812101179008)

    def test_area_provides_altitudes_extent(self):
        extent = self.area['extent']
        self.assertEqual(extent['altitudes']['max'], 45)
        self.assertEqual(extent['altitudes']['min'], 0)