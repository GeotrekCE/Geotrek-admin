from django.conf import settings
from django.test import TestCase
from django.db import connections, DEFAULT_DB_ALIAS
from django.contrib.gis.geos import LineString

from geotrek.core.models import Path
from geotrek.core.factories import TopologyFactory


class ElevationTest(TestCase):

    def setUp(self):
        # Create a simple fake DEM
        conn = connections[DEFAULT_DB_ALIAS]
        cur = conn.cursor()
        cur.execute('CREATE TABLE mnt (rid serial primary key, rast raster)')
        cur.execute('INSERT INTO mnt (rast) VALUES (ST_MakeEmptyRaster(3, 3, 0, 3, 1, -1, 0, 0, %s))', [settings.SRID])
        cur.execute('UPDATE mnt SET rast = ST_AddBand(rast, \'16BSI\')')
        for x in range(1, 4):
            for y in range(1, 4):
                cur.execute('UPDATE mnt SET rast = ST_SetValue(rast, %s, %s, %s::float)', [x, y, x+y])
        conn.commit_unless_managed()

        self.path = Path.objects.create(geom=LineString((1.5,1.5), (2.5,1.5), (1.5,2.5)))

    def test_elevation_path(self):
        self.assertEqual(self.path.ascent, 1)
        self.assertEqual(self.path.descent, -2)
        self.assertEqual(self.path.min_elevation, 3)
        self.assertEqual(self.path.max_elevation, 5)
        self.assertEqual(len(self.path.geom_3d.coords), 3)

    def test_elevation_profile(self):
        profile = self.path.get_elevation_profile()
        self.assertEqual(len(profile), 3)
        self.assertEqual(profile[0][0], 0.0)
        self.assertTrue(2.41421 < profile[-1][0] < 2.41422)
        self.assertTrue(profile[0][2], 4)
        self.assertTrue(profile[1][2], 5)
        self.assertTrue(profile[2][2], 3)

    def test_elevation_topology_line(self):
        topo = TopologyFactory.create(no_path=True)
        topo.add_path(self.path, start=0.2, end=0.7)
        topo.save()

        self.assertEqual(topo.ascent, 1)
        self.assertEqual(topo.descent, -1)
        self.assertEqual(topo.min_elevation, 4)
        self.assertEqual(topo.max_elevation, 5)
        self.assertEqual(len(topo.geom_3d.coords), 3)

    def test_elevation_topology_point(self):
        topo = TopologyFactory.create(no_path=True)
        topo.add_path(self.path, start=0.5, end=0.5)
        topo.save()

        self.assertEqual(topo.ascent, 0)
        self.assertEqual(topo.descent, 0)
        self.assertEqual(topo.min_elevation, 5)
        self.assertEqual(topo.max_elevation, 5)