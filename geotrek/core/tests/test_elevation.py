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

    def test_elevation_path(self):
        # Create a geometry and check elevation-based indicators
        p = Path(geom=LineString((1.5,1.5,0), (2.5,1.5,0), (1.5,2.5,0)))
        self.assertEqual(p.ascent, 0)
        self.assertEqual(p.descent, 0)
        self.assertEqual(p.min_elevation, 0)
        self.assertEqual(p.max_elevation, 0)
        p.save()
        self.assertEqual(p.ascent, 1)
        self.assertEqual(p.descent, -2)
        self.assertEqual(p.min_elevation, 3)
        self.assertEqual(p.max_elevation, 5)

        # Check elevation profile
        profile = p.get_elevation_profile()
        self.assertEqual(len(profile), 4)  # minimum possible (since p.length < sampling resolution)
        self.assertEqual(profile[0][0], 0.0)
        self.assertEqual(profile[0][3], 4)
        self.assertTrue(2.4 < profile[-1][0] < 2.5)  # p.geom.length
        self.assertEqual(profile[-1][3], 3)

    def test_elevation_topology_line(self):
        p = Path(geom=LineString((1.5,1.5,0), (2.5,1.5,0), (1.5,2.5,0)))
        p.save()

        topo = TopologyFactory.create(no_path=True)
        topo.add_path(p, start=0.2, end=0.7)
        topo.save()

        self.assertEqual(topo.ascent, 0)
        self.assertEqual(topo.descent, 0)
        self.assertEqual(topo.min_elevation, 4)
        self.assertEqual(topo.max_elevation, 5)

    def test_elevation_topology_point(self):
        p = Path(geom=LineString((1.5,1.5,0), (2.5,1.5,0), (1.5,2.5,0)))
        p.save()

        topo = TopologyFactory.create(no_path=True)
        topo.add_path(p, start=0.5, end=0.5)
        topo.save()

        self.assertEqual(topo.ascent, 0)
        self.assertEqual(topo.descent, 0)
        self.assertEqual(topo.min_elevation, 5)
        self.assertEqual(topo.max_elevation, 5)