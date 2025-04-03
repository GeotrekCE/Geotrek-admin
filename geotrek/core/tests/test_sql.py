from unittest import skipIf

from django.conf import settings
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
