from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import WKBReader
from django.db import connection
from django.test import TestCase

from geotrek.authent.tests.factories import StructureFactory
from geotrek.core.models import Path, PathAggregation, Topology, Trail
from geotrek.core.tests.factories import PathFactory, TopologyFactory


class SQLDefaultValuesTest(TestCase):
    def test_path(self):
        path = PathFactory.build()
        structure = StructureFactory.create()
        with connection.cursor() as cur:
            cur.execute(f"""INSERT INTO core_path
                           (
                           geom,
                           structure_id
                           ) VALUES
                           (
                           ST_GeomFromEWKT(\'{path.geom.ewkt}\'),
                           {structure.pk}
                           )""")
        path = Path.objects.first()
        self.assertTrue(path.valid)

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_topology(self):
        path = PathFactory.create()
        with connection.cursor() as cur:
            cur.execute("""INSERT INTO core_topology DEFAULT VALUES""")

        topology = Topology.objects.first()
        topology.add_path(path, 0, 1)
        self.assertEqual(topology.geom, path.geom)
        self.assertEqual(topology.kind, "")

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_pathaggregation(self):
        path = PathFactory.create()
        topology = TopologyFactory.create(paths=[])
        self.assertIsNone(topology.geom)
        with connection.cursor() as cur:
            cur.execute(f"""INSERT INTO core_pathaggregation
                           (
                           path_id,
                           topo_object_id
                           ) VALUES
                           (
                           {path.pk},
                           {topology.pk}
                           )""")
        topology.reload()
        first, last = path.geom.boundary
        self.assertEqual(topology.geom, first)
        path_aggregation = PathAggregation.objects.first()
        self.assertEqual(path_aggregation.order, 0)

    def test_trail(self):
        topology = TopologyFactory.create()
        structure = StructureFactory.create()
        with connection.cursor() as cur:
            cur.execute(f"""INSERT INTO core_trail
                                  (
                                  name,
                                  topo_object_id,
                                  structure_id
                                  ) VALUES
                                  (
                                  'name_trail',
                                  {topology.pk},
                                  {structure.pk}
                                  )""")
        trail = Trail.objects.first()
        self.assertEqual(trail.departure, "")


class STExtendTest(TestCase):
    head_rate = 1
    head_constant = 2
    tail_rate = 1
    tail_constant = 2
    srid = 2154

    def execute_extend(self, line):
        cursor = connection.cursor()
        sql = f"""
                SELECT st_extend(ST_GeomFromText('{line}',{self.srid}), {self.head_rate}, {self.head_constant}, {self.tail_rate}, {self.tail_constant})
                """
        cursor.execute(sql)
        result = cursor.fetchall()
        wkb_r = WKBReader()
        geom = wkb_r.read(result[0][0])
        return geom

    def test_linestring_2_points(self):
        line = "LINESTRING(0 0, 10 0)"
        extend_line = self.execute_extend(line)

        self.assertAlmostEqual(extend_line.coords[0][0], -2, places=5)
        self.assertAlmostEqual(extend_line.coords[0][1], 0, places=5)
        self.assertAlmostEqual(extend_line.coords[1][0], 12, places=5)
        self.assertAlmostEqual(extend_line.coords[1][1], 0, places=5)

    def test_linestring_3_points(self):
        line = "LINESTRING(0 0, 5 0, 10 0)"
        extend_line = self.execute_extend(line)

        self.assertAlmostEqual(extend_line.coords[0][0], -2, places=5)
        self.assertAlmostEqual(extend_line.coords[0][1], 0, places=5)
        self.assertAlmostEqual(extend_line.coords[1][0], 5, places=5)
        self.assertAlmostEqual(extend_line.coords[1][1], 0, places=5)
        self.assertAlmostEqual(extend_line.coords[2][0], 12, places=5)
        self.assertAlmostEqual(extend_line.coords[2][1], 0, places=5)

    def test_linestring_3_points_not_aligned(self):
        line = "LINESTRING(0 0, 5 5, 10 0)"
        extend_line = self.execute_extend(line)

        self.assertAlmostEqual(extend_line.coords[0][0], -1.414213, places=5)
        self.assertAlmostEqual(extend_line.coords[0][1], -1.414213, places=5)
        self.assertAlmostEqual(extend_line.coords[1][0], 5, places=5)
        self.assertAlmostEqual(extend_line.coords[1][1], 5, places=5)
        self.assertAlmostEqual(extend_line.coords[2][0], 11.414213, places=5)
        self.assertAlmostEqual(extend_line.coords[2][1], -1.414213, places=5)

    def test_closed_linestring(self):
        line = "LINESTRING(0 0, 5 0, 5 5, 0 0)"
        extend_line = self.execute_extend(line)

        self.assertAlmostEqual(extend_line.coords[0][0], -2, places=5)
        self.assertAlmostEqual(extend_line.coords[0][1], 0, places=5)
        self.assertAlmostEqual(extend_line.coords[1][0], 5, places=5)
        self.assertAlmostEqual(extend_line.coords[1][1], 0, places=5)
        self.assertAlmostEqual(extend_line.coords[2][0], 5, places=5)
        self.assertAlmostEqual(extend_line.coords[2][1], 5, places=5)
        self.assertAlmostEqual(extend_line.coords[3][0], -1.414213, places=5)
        self.assertAlmostEqual(extend_line.coords[3][1], -1.414213, places=5)
