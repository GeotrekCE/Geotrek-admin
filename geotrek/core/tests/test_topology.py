import json
import math
from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from django.db import DEFAULT_DB_ALIAS, connections
from django.test import TestCase

from geotrek.common.tests.mixins import dictfetchall
from geotrek.common.utils import dbnow
from geotrek.core.models import Path, PathAggregation, Topology
from geotrek.core.tests.factories import (
    PathAggregationFactory,
    PathFactory,
    TopologyFactory,
)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class TopologyTest(TestCase):
    def test_geom_null_is_safe(self):
        t = TopologyFactory.create()
        t.geom = None
        t.save()
        self.assertNotEqual(t.geom, None)

    def test_dates(self):
        t1 = dbnow()
        e = TopologyFactory.build()
        e.save()
        t2 = dbnow()
        self.assertTrue(t1 < e.date_insert < t2)

        e.delete()
        t3 = dbnow()
        self.assertTrue(t2 < e.date_update < t3)

    def test_latestupdate_delete(self):
        TopologyFactory.create_batch(10)
        t1 = dbnow()
        self.assertTrue(t1 > Topology.objects.latest("date_update").date_update)
        Topology.objects.first().delete(force=True)
        self.assertFalse(t1 > Topology.objects.latest("date_update").date_update)

    def test_length(self):
        e = TopologyFactory.build()
        self.assertEqual(e.length, 0)
        e.save()
        self.assertEqual(e.length, 0)
        PathAggregationFactory.create(topo_object=e)
        e.save()
        self.assertNotEqual(e.length, 0)

    def test_length_2d(self):
        e = TopologyFactory.build()
        e.save()
        topology = Topology.objects.get(pk=e.pk)
        self.assertEqual(topology.length_2d, 0)

    def test_kind(self):
        from geotrek.land.models import LandEdge
        from geotrek.land.tests.factories import LandEdgeFactory

        # Test with a concrete inheritance of Topology : LandEdge
        self.assertEqual("TOPOLOGY", Topology.KIND)
        self.assertEqual(0, Topology.objects.filter(kind="LANDEDGE").count())
        self.assertEqual("LANDEDGE", LandEdge.KIND)
        # Kind of instances
        e = LandEdgeFactory.create()
        self.assertEqual(e.kind, LandEdge.KIND)
        self.assertEqual(1, Topology.objects.filter(kind="LANDEDGE").count())

    def test_link_closest_visible_path(self):
        """
        Topology must be linked to the closest visible path only
        """
        path_visible = Path(
            name="visible", geom="LINESTRING(0 0, 1 0, 2 0)", visible=True
        )
        path_visible.save()
        path_unvisible = Path(
            name="unvisible", geom="LINESTRING(0 3, 1 3, 2 3)", visible=False
        )
        path_unvisible.save()

        # default manager see 1 path
        self.assertEqual(Path.objects.count(), 1)

        # custom manager see 2 paths
        self.assertEqual(Path.include_invisible.count(), 2)

        # create topo on visible path
        topology = Topology._topologypoint(0, 0, None)
        topology.save()

        # because FK and M2M are used with default manager only, others tests are in SQL
        conn = connections[DEFAULT_DB_ALIAS]
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT t.id as id_path,
                   et.topo_object_id as id_topology,
                   t.visible as visible
            FROM core_pathaggregation et
            JOIN core_path t ON et.path_id=t.id
            WHERE et.topo_object_id={topology.pk}
            """
        )

        datas = dictfetchall(cur)

        # topo must be linked to visible path
        self.assertIn(topology.pk, [ele["id_topology"] for ele in datas], f"{datas}")
        self.assertIn(path_visible.pk, [ele["id_path"] for ele in datas], f"{datas}")
        self.assertNotIn(
            path_unvisible.pk, [ele["id_path"] for ele in datas], f"{datas}"
        )

        # new topo on invible path
        topology = Topology._topologypoint(0, 3, None)
        topology.save()

        cur.execute(
            f"""
            SELECT t.id as id_path,
                   et.topo_object_id as id_topology,
                   t.visible as visible
            FROM core_pathaggregation et
            JOIN core_path t ON et.path_id=t.id
            WHERE et.topo_object_id={topology.pk}
            """
        )

        datas = dictfetchall(cur)

        self.assertIn(topology.pk, [ele["id_topology"] for ele in datas], f"{datas}")
        self.assertIn(path_visible.pk, [ele["id_path"] for ele in datas], f"{datas}")
        self.assertNotIn(
            path_unvisible.pk, [ele["id_path"] for ele in datas], f"{datas}"
        )
        cur.close()

    def test_topology_linked_to_not_draft(self):
        path_draft = PathFactory.create(
            name="draft", geom="LINESTRING(0 0, 1 0, 2 0)", draft=True
        )
        path_draft.save()
        path_normal = PathFactory.create(
            name="normal", geom="LINESTRING(0 3, 1 3, 2 3)", draft=False
        )
        path_normal.save()
        point = Point(0, 0, srid=settings.SRID)
        closest = Path.closest(point)
        self.assertEqual(point.wkt, "POINT (0 0)")
        self.assertEqual(closest, path_normal)

    def test_topology_deserialize(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (2, 2)))
        p2 = PathFactory.create(geom=LineString((2, 2), (2, 0)))
        p3 = PathFactory.create(geom=LineString((2, 0), (4, 0)))
        pks = [p.pk for p in [p1, p2, p3]]
        Topology.deserialize(
            f'{{"paths": {pks}, "positions": {{"0": [0.3, 1.0], "2": [0.0, 0.7]}}, "offset": 1}}'
        )
        self.assertEqual(Path.objects.count(), 3)

    def test_topology_deserialize_point(self):
        PathFactory.create(geom=LineString((699999, 6600001), (700001, 6600001)))
        topology = Topology.deserialize('{"lat": 46.5, "lng": 3}')
        self.assertEqual(topology.offset, -1)
        self.assertEqual(topology.aggregations.count(), 1)
        self.assertEqual(topology.aggregations.get().start_position, 0.5)
        self.assertEqual(topology.aggregations.get().end_position, 0.5)

    def test_topology_deserialize_point_with_snap(self):
        path = PathFactory.create(geom=LineString((699999, 6600001), (700001, 6600001)))
        topology = Topology.deserialize(f'{{"lat": 46.5, "lng": 3, "snap": {path.pk}}}')
        self.assertEqual(topology.offset, 0)
        self.assertEqual(topology.aggregations.count(), 1)
        self.assertEqual(topology.aggregations.get().start_position, 0.5)
        self.assertEqual(topology.aggregations.get().end_position, 0.5)

    def test_topology_deserialize_inexistant(self):
        with self.assertRaises(Topology.DoesNotExist):
            Topology.deserialize("4012999999")

    def test_topology_deserialize_inexistant_point(self):
        PathFactory.create(geom=LineString((699999, 6600001), (700001, 6600001)))
        Topology.deserialize('{"lat": 46.5, "lng": 3, "pk": 4012999999}')

    def test_topology_deserialize_inexistant_line(self):
        path = PathFactory.create(geom=LineString((699999, 6600001), (700001, 6600001)))
        Topology.deserialize(
            f'[{{"pk": 4012999999, "paths": [{path.pk}], "positions": {{"0": [0.0, 1.0]}}, "offset": 1}}]'
        )

    def test_topology_deserialize_invalid(self):
        with self.assertRaises(ValueError):
            Topology.deserialize(
                '[{"paths": [4012999999], "positions": {}, "offset": 1}]'
            )


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class TopologyDeletionTest(TestCase):
    def test_deleted_is_hidden_but_still_exists(self):
        topology = TopologyFactory.create(offset=1)
        path = topology.paths.get()
        self.assertEqual(
            PathAggregation.objects.filter(topo_object=topology).count(), 1
        )
        self.assertEqual(path.topology_set.all().count(), 1)
        topology.delete()
        # Make sure object remains in database with deleted status
        self.assertEqual(
            PathAggregation.objects.filter(topo_object=topology).count(), 1
        )
        # Make sure object has deleted status
        self.assertTrue(topology.deleted)
        # Make sure object still exists
        self.assertEqual(path.topology_set.all().count(), 1)
        self.assertIn(topology, Topology.objects.all())
        # Make sure object can be hidden from managers
        self.assertNotIn(topology, Topology.objects.existing())
        self.assertEqual(path.topology_set.existing().count(), 0)

    def test_deleted_when_all_path_are_deleted(self):
        topology = TopologyFactory.create()
        self.assertFalse(topology.deleted)

        for path in topology.paths.all():
            path.delete()

        topology.reload()
        self.assertTrue(topology.deleted)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class TopologyMutateTest(TestCase):
    def test_mutate(self):
        topology1 = TopologyFactory.create(paths=[])
        self.assertEqual(topology1.paths.all().count(), 0)
        topology2 = TopologyFactory.create(offset=14.5)
        self.assertEqual(topology2.paths.all().count(), 1)
        # Normal usecase
        topology1.mutate(topology2)
        self.assertEqual(topology1.offset, 14.5)
        self.assertEqual(topology1.paths.all().count(), 1)

    def test_mutate_intersection(self):
        # Mutate a Point topology at an intersection, and make sure its aggregations
        # are not duplicated (c.f. SQL triggers)

        # Create a 3 paths intersection
        PathFactory.create(geom=LineString((0, 0), (1, 0)))
        p2 = PathFactory.create(geom=LineString((1, 0), (2, 0)))
        PathFactory.create(geom=LineString((1, 0), (1, 1)))
        # Create a topology point at this intersection
        topology = TopologyFactory.create(paths=[(p2, 0, 0)])
        self.assertTrue(topology.ispoint())
        # Make sure, the trigger worked, and linked to 3 paths
        self.assertEqual(topology.paths.all().count(), 3)
        # Mutate it to another one !
        topology2 = TopologyFactory.create(paths=[])
        self.assertEqual(topology2.paths.all().count(), 0)
        self.assertTrue(topology2.ispoint())
        topology2.mutate(topology)
        self.assertEqual(topology2.paths.all().count(), 3)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class TopologyPointTest(TestCase):
    def test_point_geom_3d(self):
        """
           +
          / \
         / X \
        +     +
        """
        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        PathFactory.create(geom=LineString((4, 4), (8, 0)))

        poi = Point(3, 1, srid=settings.SRID)
        position, distance = Path.interpolate(p1, poi)
        self.assertAlmostEqual(0.5, position, places=6)
        self.assertAlmostEqual(-1.414, distance, places=2)
        # Verify that deserializing this, we obtain the same original coordinates
        # (use lat/lng as in forms)
        poi.transform(settings.API_SRID)
        poitopo = Topology.deserialize({"lat": poi.y, "lng": poi.x})
        # Computed topology properties match original interpolation
        self.assertAlmostEqual(
            0.5, poitopo.aggregations.all()[0].start_position, places=6
        )
        self.assertAlmostEqual(-1.414, poitopo.offset, places=2)
        # Resulting geometry
        self.assertAlmostEqual(3, poitopo.geom.x, places=6)
        self.assertAlmostEqual(1, poitopo.geom.y, places=6)

    def test_point_geom_not_moving(self):
        r"""
        Modify path, point not moving
        +                  +
        |                  |
         \     X          /        X
         /                \
        |                  |
        +                  +
        """
        p1 = PathFactory.create(
            geom=LineString((0, 0), (0, 5), (5, 10), (0, 15), (0, 20))
        )
        poi = Point(10, 10, srid=settings.SRID)
        poi.transform(settings.API_SRID)
        poitopo = Topology.deserialize({"lat": poi.y, "lng": poi.x})
        self.assertEqual(0.5, poitopo.aggregations.all()[0].start_position)
        self.assertAlmostEqual(-5, poitopo.offset, places=6)
        # It should have kept its position !
        self.assertAlmostEqual(10, poitopo.geom.x, places=6)
        self.assertAlmostEqual(10, poitopo.geom.y, places=6)
        # Change path, it should still be in the same position
        p1.geom = LineString((0, 0), (0, 5), (-5, 10), (0, 15), (0, 20))
        p1.save()
        poitopo.reload()
        self.assertAlmostEqual(10, poitopo.geom.x, places=6)
        self.assertAlmostEqual(10, poitopo.geom.y, places=6)

    def test_point_offset_kept(self):
        """
        Shorten path, offset kept.

          X                        X
        +-----------+            +------+

        """
        p1 = PathFactory.create(geom=LineString((0, 0), (20, 0)))
        poi = Point(5, 10, srid=settings.SRID)
        poi.transform(settings.API_SRID)
        poitopo = Topology.deserialize({"lat": poi.y, "lng": poi.x})
        self.assertAlmostEqual(
            0.25, poitopo.aggregations.all()[0].start_position, places=6
        )
        self.assertAlmostEqual(10, poitopo.offset, places=6)

        p1.geom = LineString((0, 0), (10, 0))
        p1.save()
        poitopo.reload()

        self.assertAlmostEqual(10, poitopo.offset, places=6)
        # Not moved:
        self.assertAlmostEqual(5, poitopo.geom.x, places=6)
        self.assertAlmostEqual(10, poitopo.geom.y, places=6)

    def test_point_offset_updated(self):
        """
        Shorten path, offset updated.

               X                              X
        +-----------+            +------+

        """
        p1 = PathFactory.create(geom=LineString((0, 0), (20, 0)))
        poi = Point(10, 10, srid=settings.SRID)
        poi.transform(settings.API_SRID)
        poitopo = Topology.deserialize({"lat": poi.y, "lng": poi.x})
        poitopo.save()
        self.assertAlmostEqual(
            0.5, poitopo.aggregations.all()[0].start_position, places=6
        )
        self.assertAlmostEqual(10, poitopo.offset, places=6)

        p1.geom = LineString((0, 0), (0, 5))
        p1.save()
        poitopo.reload()
        self.assertAlmostEqual(-11.180339887, poitopo.offset, places=6)
        # Not moved:
        self.assertAlmostEqual(10, poitopo.geom.x, places=6)
        self.assertAlmostEqual(10, poitopo.geom.y, places=6)

    def test_point_geom_moving(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (0, 5)))
        poi = Point(0, 2.5, srid=settings.SRID)
        poi.transform(settings.API_SRID)
        poitopo = Topology.deserialize({"lat": poi.y, "lng": poi.x})
        poitopo.save()
        self.assertAlmostEqual(
            0.5, poitopo.aggregations.all()[0].start_position, places=6
        )
        self.assertAlmostEqual(0, poitopo.offset, places=6)
        self.assertAlmostEqual(0, poitopo.geom.x, places=6)
        self.assertAlmostEqual(2.5, poitopo.geom.y, places=6)
        p1.geom = LineString((10, 0), (10, 5))
        p1.save()
        poitopo.reload()
        self.assertAlmostEqual(10, poitopo.geom.x, places=6)
        self.assertAlmostEqual(2.5, poitopo.geom.y, places=6)

    def test_junction_point(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (2, 2)))
        p2 = PathFactory.create(geom=LineString((0, 0), (2, 0)))
        p3 = PathFactory.create(geom=LineString((0, 2), (0, 0)))

        # Create a junction point topology
        t = TopologyFactory.create(paths=[])
        self.assertEqual(t.paths.all().count(), 0)

        pa = PathAggregationFactory.create(
            topo_object=t, path=p1, start_position=0.0, end_position=0.0
        )

        self.assertCountEqual(t.paths.all(), [p1, p2, p3])

        # Update to a non junction point topology
        pa.end_position = 0.4
        pa.save()

        self.assertCountEqual(t.paths.all(), [p1])

        # Update to a junction point topology
        pa.end_position = 0.0
        pa.save()

        self.assertCountEqual(t.paths.all(), [p1, p2, p3])

    def test_point_at_end_of_path_not_moving_after_mutate(self):
        PathFactory.create(geom=LineString((400, 400), (410, 400), srid=settings.SRID))
        self.assertEqual(1, Path.objects.all().count())

        father = Topology.deserialize({"lat": -1, "lng": -1})
        father.save()

        poi = Point(500, 600, srid=settings.SRID)
        poi.transform(settings.API_SRID)
        son = Topology.deserialize({"lat": poi.y, "lng": poi.x})
        father.mutate(son)
        self.assertAlmostEqual(father.geom.x, 500, places=6)
        self.assertAlmostEqual(father.geom.y, 600, places=6)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class TopologyLineTest(TestCase):
    def test_topology_geom(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (2, 2)))
        p2 = PathFactory.create(geom=LineString((2, 2), (2, 0)))
        p3 = PathFactory.create(geom=LineString((2, 0), (4, 0)))

        # Type Point
        t = TopologyFactory.create(paths=[(p1, 0.5, 0.5)])
        self.assertEqual(t.geom, Point((1, 1), srid=settings.SRID))

        # 50% of path p1, 100% of path p2
        t = TopologyFactory.create(paths=[(p1, 0.5, 1), p2])
        self.assertEqual(t.geom, LineString((1, 1), (2, 2), (2, 0), srid=settings.SRID))

        # 100% of path p2 and p3, with offset of 1
        t = TopologyFactory.create(offset=1, paths=[p2, p3])
        self.assertEqual(t.geom, LineString((3, 2), (3, 1), (4, 1), srid=settings.SRID))

        # Change offset, geometry is computed again
        t.offset = 0.5
        t.save()
        self.assertEqual(
            t.geom, LineString((2.5, 2), (2.5, 0.5), (4, 0.5), srid=settings.SRID)
        )

    def test_topology_geom_should_not_be_sampled(self):
        coords = [(x, math.sin(x)) for x in range(100)]
        sampled_3d = [(x, math.sin(x), math.cos(x)) for x in range(0, 100, 5)]
        p1 = PathFactory.create(geom=LineString(*coords))
        p1.geom_3d = LineString(*sampled_3d)
        p1.save(update_fields=["geom_3d"])

        t = TopologyFactory.create(paths=[p1])

        self.assertEqual(len(t.geom.coords), 100)

    def test_topology_geom_with_intermediate_markers(self):
        # Intermediate (forced passage) markers for topologies
        # Use a bifurcation, make sure computed geometry is correct
        #       +--p2---+
        #   +---+-------+---+
        #     p1   p3     p4
        p1 = PathFactory.create(geom=LineString((0, 0), (2, 0)))
        p2 = PathFactory.create(geom=LineString((2, 0), (2, 1), (4, 1), (4, 0)))
        p3 = PathFactory.create(geom=LineString((2, 0), (4, 0)))
        p4 = PathFactory.create(geom=LineString((4, 0), (6, 0)))
        """
        From p1 to p4, with point in the middle of p3
        """
        t = TopologyFactory.create(paths=[p1, p3, (p3, 0.5, 0.5), p4])
        self.assertEqual(
            t.geom, LineString((0, 0), (2, 0), (4, 0), (6, 0), srid=settings.SRID)
        )
        """
        From p1 to p4, through p2
        """
        t = TopologyFactory.create(paths=[p1, p2, (p2, 0.5, 0.5), p4])
        self.assertEqual(
            t.geom,
            LineString(
                (0, 0), (2, 0), (2, 1), (4, 1), (4, 0), (6, 0), srid=settings.SRID
            ),
        )

        """
        From p1 to p4, though p2, but **with start/end at 0.0**
        """
        t2 = TopologyFactory.create(paths=[p1, p2, (p2, 0, 0), p4])
        self.assertEqual(t2.geom, t.geom)

    def test_path_geom_update(self):
        # Create a path
        p = PathFactory.create(geom=LineString((0, 0), (4, 0)))

        # Create a linear topology
        t1 = TopologyFactory.create(offset=1, paths=[(p, 0, 0.5)])
        t1_agg = t1.aggregations.get()

        # Create a point topology
        t2 = TopologyFactory.create(offset=-1, paths=[(p, 0.5, 0.5)])
        t2_agg = t2.aggregations.get()

        # Ensure linear topology is correct before path modification
        self.assertEqual(t1.offset, 1)
        self.assertEqual(t1.geom.coords, ((0, 1), (2, 1)))
        self.assertEqual(t1_agg.start_position, 0.0)
        self.assertEqual(t1_agg.end_position, 0.5)

        # Ensure point topology is correct before path modification
        self.assertEqual(t2.offset, -1)
        self.assertEqual(t2.geom.coords, (2, -1))
        self.assertEqual(t2_agg.start_position, 0.5)
        self.assertEqual(t2_agg.end_position, 0.5)

        # Modify path geometry and refresh computed data
        p.geom = LineString((0, 2), (8, 2))
        p.save()
        t1.reload()
        t1_agg = t1.aggregations.get()
        t2.reload()
        t2_agg = t2.aggregations.get()

        # Ensure linear topology is correct after path modification
        self.assertEqual(t1.offset, 1)
        self.assertEqual(t1.geom.coords, ((0, 3), (4, 3)))
        self.assertEqual(t1_agg.start_position, 0.0)
        self.assertEqual(t1_agg.end_position, 0.5)

        # Ensure point topology is correct before path modification
        self.assertEqual(t2.offset, -3)
        self.assertEqual(t2.geom.coords, (2, -1))
        self.assertEqual(t2_agg.start_position, 0.25)
        self.assertEqual(t2_agg.end_position, 0.25)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class TopologyCornerCases(TestCase):
    def test_opposite_paths(self):
        """
                A  C
        B +-------+-------+ D

        """
        ab = PathFactory.create(geom=LineString((5, 0), (0, 0)))
        cd = PathFactory.create(geom=LineString((5, 0), (10, 0)))
        topo = TopologyFactory.create(paths=[(ab, 0.2, 0), (cd, 0, 0.2)])
        expected = LineString((4, 0), (5, 0), (6, 0), srid=settings.SRID)
        self.assertEqual(topo.geom, expected)
        # Now let's have some fun, reverse BA :)
        ab.reverse()
        ab.save()
        topo.reload()
        self.assertEqual(topo.geom, expected)

    def test_opposite_paths_with_middle(self):
        """
                A            C
        B +-------+--------+-------+ D

        """
        ab = PathFactory.create(geom=LineString((5, 0), (0, 0)))
        ac = PathFactory.create(geom=LineString((5, 0), (10, 0)))
        cd = PathFactory.create(geom=LineString((10, 0), (15, 0)))
        topo = TopologyFactory.create(paths=[(ab, 0.2, 0), ac, (cd, 0, 0.2)])
        expected = LineString((4, 0), (5, 0), (10, 0), (11, 0), srid=settings.SRID)
        self.assertEqual(topo.geom, expected)
        # Reverse AC ! OMG this is hell !
        ac.reverse()
        ac.save()
        topo.reload()
        self.assertEqual(topo.geom, expected)

    def test_return_path(self):
        """
                     A
                 ----+
                 |
        B +------+------+ C
        """
        p1 = PathFactory.create(geom=LineString((0, 0), (10, 0)))
        p2 = PathFactory.create(geom=LineString((5, 0), (5, 10), (10, 10)))
        p3 = Path.objects.filter(name=p1.name).exclude(pk=p1.pk)[0]  # Was splitted :)
        # Now create a topology B-A-C
        topo = TopologyFactory.create(
            paths=[
                (p1, 0.5, 1),
                (p2, 0, 0.8),
                (p2, 0.8, 0.8),
                (p2, 0.8, 0),
                (p3, 0, 0.5),
            ]
        )
        self.assertEqual(
            topo.geom,
            LineString(
                (2.5, 0),
                (5, 0),
                (5, 10),
                (7, 10),
                (5, 10),
                (5, 0),
                (7.5, 0),
                srid=settings.SRID,
            ),
        )

    def test_return_path_serialized(self):
        """
        Same as test_return_path() but from deserialization.
        """
        p1 = PathFactory.create(geom=LineString((0, 0), (10, 0)))
        p2 = PathFactory.create(geom=LineString((5, 0), (5, 10), (10, 10)))
        p3 = Path.objects.filter(name=p1.name).exclude(pk=p1.pk)[0]  # Was splitted :)
        topo = Topology.deserialize(
            f"""
           [{{"offset":0,
             "positions":{{"0":[0.5,1],
                          "1":[0.0, 0.8]}},
             "paths":[{p1.pk},{p2.pk}]
            }},
            {{"offset":0,
             "positions":{{"0":[0.8,0.0],
                          "1":[0.0, 0.5]}},
             "paths":[{p2.pk},{p3.pk}]
            }}
           ]
        """
        )
        topo.kind = "TOPOLOGY"
        topo.save()
        self.assertEqual(
            topo.geom,
            LineString(
                (2.5, 0),
                (5, 0),
                (5, 10),
                (7, 10),
                (5, 10),
                (5, 0),
                (7.5, 0),
                srid=settings.SRID,
            ),
        )


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class TopologyLoopTests(TestCase):
    def test_simple_loop(self):
        """
           ==========
          ||        ||
        A +==------==+ B
        """
        p1 = PathFactory.create(geom=LineString((10, 0), (0, 0)))
        p2 = PathFactory.create(geom=LineString((0, 0), (0, 5), (10, 5), (10, 0)))
        # Full loop
        topo = TopologyFactory.create(paths=[p1, p2])
        self.assertEqual(
            topo.geom,
            LineString((10, 0), (0, 0), (0, 5), (10, 5), (10, 0), srid=settings.SRID),
        )
        # Subpart, like in diagram
        topo = TopologyFactory.create(paths=[(p1, 0.8, 1), p2, (p1, 0, 0.2)])
        self.assertEqual(
            topo.geom,
            LineString(
                (2, 0), (0, 0), (0, 5), (10, 5), (10, 0), (8, 0), srid=settings.SRID
            ),
        )

    def test_trek_loop(self):
        """
                            =========
                           ||       ||
        +-------===========+=========+----------+
        """
        p1 = PathFactory.create(geom=LineString((0, 0), (10, 0)))
        p2 = PathFactory.create(geom=LineString((10, 0), (30, 0)))
        p3 = PathFactory.create(geom=LineString((10, 0), (10, 5), (20, 5), (20, 0)))
        topo = TopologyFactory.create(
            paths=[(p1, 0.3, 1), p3, (p2, 1, 0), (p1, 1, 0.3)]
        )
        self.assertEqual(
            topo.geom,
            LineString(
                (3, 0),
                (10, 0),
                (10, 5),
                (20, 5),
                (20, 0),
                (10, 0),
                (3, 0),
                srid=settings.SRID,
            ),
        )

    def test_spoon_loop(self):
        """
                            =====<====
                           ||       ||
        +-------===<===>===+=====>===
        """
        p1 = PathFactory.create(geom=LineString((0, 0), (10, 0)))
        p2 = PathFactory.create(
            geom=LineString((10, 0), (10, 5), (20, 5), (20, 0), (10, 0))
        )
        topo = TopologyFactory.create(
            paths=[
                (p1, 0.3, 1),
                (p2, 1, 0.4),
                (p2, 0.4, 0.4),
                (p2, 0.4, 0.2),
                (p2, 0.2, 0.2),
                (p2, 0.2, 0),
                (p1, 1, 0.3),
            ]
        )
        self.assertEqual(
            topo.geom,
            LineString(
                (3, 0),
                (10, 0),
                (20, 0),
                (20, 5),
                (17, 5),
                (11, 5),  # extra point due middle aggregation
                (10, 5),
                (10, 0),
                (3, 0),
                srid=settings.SRID,
            ),
        )

        # Deserializing should work too
        topod = Topology.deserialize(
            f"""
           [{{"positions":{{"0":[0.3,1],"1":[1, 0.4]}},"paths":[{p1.pk},{p2.pk}]}},
            {{"positions":{{"0":[0.4, 0.2]}},"paths":[{p2.pk}]}},
            {{"positions":{{"0":[0.2,0],"1":[1,0.3]}},"paths":[{p2.pk},{p1.pk}]}}]"""
        )
        topod.kind = "TOPOLOGY"
        topod.save()
        self.assertEqual(topo.geom, topod.geom)
        self.assertEqual(topod.aggregations.all().count(), 7)

    def test_spoon_loop_2(self):
        """
                            =====>====
                           ||       ||
        +-------===<===>===+=====<===
        """
        p1 = PathFactory.create(geom=LineString((0, 0), (10, 0)))
        p2 = PathFactory.create(
            geom=LineString((10, 0), (10, 5), (20, 5), (20, 0), (10, 0))
        )
        topo = TopologyFactory.create(
            paths=[
                (p1, 0.3, 1),
                (p2, 0, 0.4),
                (p2, 0.4, 0.4),
                (p2, 0.4, 0.8),
                (p2, 0.8, 0.8),
                (p2, 0.8, 1),
                (p1, 1, 0.3),
            ]
        )
        self.assertEqual(
            topo.geom,
            LineString(
                (3, 0),
                (10, 0),
                (10, 5),
                (17, 5),
                (20, 5),  # extra point due middle aggregation
                (20, 0),
                (16, 0),
                (10, 0),
                (3, 0),
                srid=settings.SRID,
            ),
        )

        # De/Serializing should work too
        serialized = f"""
           [{{"kind": "TOPOLOGY","positions":{{"0":[0.3,1],"1":[0, 0.4]}},"paths":[{p1.pk},{p2.pk}],"offset": 0.0,"pk": {topo.pk}}},
            {{"kind": "TOPOLOGY","positions":{{"0":[0.4, 0.8]}},"paths":[{p2.pk}],"offset": 0.0,"pk": {topo.pk}}},
            {{"kind": "TOPOLOGY","positions":{{"0":[0.8,1],"1":[1,0.3]}},"paths":[{p2.pk},{p1.pk}],"offset": 0.0,"pk": {topo.pk}}}]"""

        self.assertEqual(json.loads(serialized), json.loads(topo.serialize()))
        topod = Topology.deserialize(serialized)
        self.assertEqual(topo.geom, topod.geom)
        self.assertEqual(topod.aggregations.all().count(), 7)

    def test_trek_all_reverse(self):
        """

        +----<===+=======+====|----->

        """
        p1 = PathFactory.create(geom=LineString((0, 0), (10, 0)))
        p2 = PathFactory.create(geom=LineString((10, 0), (20, 0)))
        p3 = PathFactory.create(geom=LineString((20, 0), (30, 0)))

        topo = TopologyFactory.create(paths=[(p3, 0.2, 0), (p2, 1, 0), (p1, 1, 0.9)])
        self.assertEqual(
            topo.geom,
            LineString(
                (22.0, 0.0), (20.0, 0.0), (10.0, 0.0), (9.0, 0.0), srid=settings.SRID
            ),
        )


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class TopologySerialization(TestCase):
    def test_serialize_line(self):
        path = PathFactory.create()
        test_objdict = {
            "kind": Topology.KIND,
            "offset": 1.0,
            "positions": {},
            "paths": [path.pk],
        }
        # +|========>+
        topo = TopologyFactory.create(offset=1.0, paths=[path])
        test_objdict["pk"] = topo.pk
        test_objdict["positions"]["0"] = [0.0, 1.0]
        objdict = json.loads(topo.serialize())
        self.assertDictEqual(objdict[0], test_objdict)

        # +<========|+
        topo = TopologyFactory.create(offset=1.0, paths=[(path, 1, 0)])
        test_objdict["pk"] = topo.pk
        test_objdict["positions"]["0"] = [1.0, 0.0]
        objdict = json.loads(topo.serialize())
        self.assertDictEqual(objdict[0], test_objdict)

        # +|========>+<========|+
        path2 = PathFactory.create()
        topo = TopologyFactory.create(offset=1.0, paths=[(path, 0, 1), (path2, 1, 0)])
        test_objdict["pk"] = topo.pk
        test_objdict["paths"] = [path.pk, path2.pk]
        test_objdict["positions"] = {"0": [0.0, 1.0], "1": [1.0, 0.0]}
        objdict = json.loads(topo.serialize())
        self.assertDictEqual(objdict[0], test_objdict)

        # +<========|+|========>+
        topo = TopologyFactory.create(offset=1.0, paths=[(path, 1, 0), (path2, 0, 1)])
        test_objdict["pk"] = topo.pk
        test_objdict["paths"] = [path.pk, path2.pk]
        test_objdict["positions"] = {"0": [1.0, 0.0], "1": [0.0, 1.0]}
        objdict = json.loads(topo.serialize())
        self.assertDictEqual(objdict[0], test_objdict)

    def test_serialize_point(self):
        path = PathFactory.create()
        topology = TopologyFactory.create(offset=1, paths=[(path, 0.5, 0.5)])
        fieldvalue = topology.serialize()
        # fieldvalue is like '{"lat": -5.983842291017086, "lng": -1.3630770374505987, "kind": "TOPOLOGY"}'
        field = json.loads(fieldvalue)
        self.assertEqual(field["pk"], topology.pk)
        self.assertAlmostEqual(field["lat"], 46.5004566, places=6)
        self.assertAlmostEqual(field["lng"], 3.0006428, places=6)
        self.assertEqual(field["kind"], "TOPOLOGY")

    def test_serialize_two_consecutive_forced(self):
        path1 = PathFactory.create()
        path2 = PathFactory.create()
        path3 = PathFactory.create()
        topology = TopologyFactory.create(
            paths=[path1, (path2, 0.2, 0.2), (path2, 0.4, 0.4), path3]
        )
        fieldvalue = topology.serialize()
        field = json.loads(fieldvalue)
        self.assertEqual(len(field), 2)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class TopologyDerialization(TestCase):
    def test_deserialize_foreignkey(self):
        topology = TopologyFactory.create(offset=1)
        deserialized = Topology.deserialize(topology.pk)
        self.assertEqual(topology, deserialized)

    def test_deserialize_unedited_point_topology(self):
        topology = TopologyFactory.create(offset=1)
        deserialized = Topology.deserialize({"pk": topology.pk})
        self.assertEqual(topology, deserialized)

    def test_deserialize_unedited_line_topology(self):
        topology = TopologyFactory.create(offset=1)
        deserialized = Topology.deserialize([{"pk": topology.pk}, {}])
        self.assertEqual(topology, deserialized)

    def test_deserialize_line(self):
        path = PathFactory.create()
        topology = Topology.deserialize(
            f'[{{"paths": [{path.pk}], "positions": {{"0": [0.0, 1.0]}}, "offset": 1}}]'
        )
        topology.save()
        self.assertEqual(topology.offset, 1)
        self.assertEqual(topology.kind, "TMP")
        self.assertEqual(topology.paths.all().count(), 1)
        self.assertEqual(topology.aggregations.all()[0].path, path)
        self.assertEqual(topology.aggregations.all()[0].start_position, 0.0)
        self.assertEqual(topology.aggregations.all()[0].end_position, 1.0)

    def test_deserialize_multiple_lines(self):
        # Multiple paths
        p1 = PathFactory.create(geom=LineString((0, 0), (2, 2)))
        p2 = PathFactory.create(geom=LineString((2, 2), (2, 0)))
        p3 = PathFactory.create(geom=LineString((2, 0), (4, 0)))
        pks = [p.pk for p in [p1, p2, p3]]
        topology = Topology.deserialize(
            f'{{"paths": {pks}, "positions": {{"0": [0.0, 1.0], "2": [0.0, 1.0]}}, "offset": 1}}'
        )
        for i in range(3):
            self.assertEqual(topology.aggregations.all()[i].start_position, 0.0)
            self.assertEqual(topology.aggregations.all()[i].end_position, 1.0)

        topology = Topology.deserialize(
            f'{{"paths": {pks}, "positions": {{"0": [0.3, 1.0], "2": [0.0, 0.7]}}, "offset": 1}}'
        )
        self.assertEqual(topology.aggregations.all()[0].start_position, 0.3)
        self.assertEqual(topology.aggregations.all()[0].end_position, 1.0)
        self.assertEqual(topology.aggregations.all()[1].start_position, 0.0)
        self.assertEqual(topology.aggregations.all()[1].end_position, 1.0)
        self.assertEqual(topology.aggregations.all()[2].start_position, 0.0)
        self.assertEqual(topology.aggregations.all()[2].end_position, 0.7)

    def test_deserialize_point(self):
        PathFactory.create()
        # Take a point
        p = Point(700100, 6600000, 0, srid=settings.SRID)
        p.transform(settings.API_SRID)
        closest = Path.closest(p)
        # Check closest path
        self.assertEqual(closest.geom.coords, ((700000, 6600000), (700100, 6600100)))
        # The point has same x as first point of path, and y to 0 :
        topology = Topology.deserialize(f'{{"lng": {p.x}, "lat": {p.y}}}')
        topology.save()
        self.assertAlmostEqual(topology.offset, -70.7106781, places=6)
        self.assertEqual(topology.paths.all().count(), 1)
        pagg = topology.aggregations.get()
        self.assertAlmostEqual(pagg.start_position, 0.5, places=6)
        self.assertAlmostEqual(pagg.end_position, 0.5, places=6)

    def test_deserialize_serialize(self):
        path = PathFactory.create(geom=LineString((1, 1), (2, 2), (2, 0)))
        before = TopologyFactory.create(offset=1, paths=[(path, 0.5, 0.5)])

        # Deserialize its serialized version !
        after = Topology.deserialize(before.serialize())

        self.assertEqual(before.paths.all().count(), after.paths.all().count())
        start_before = before.aggregations.all()[0].start_position
        end_before = before.aggregations.all()[0].end_position
        start_after = after.aggregations.all()[0].start_position
        end_after = after.aggregations.all()[0].end_position
        self.assertAlmostEqual(start_before, start_after, places=6)
        self.assertAlmostEqual(end_before, end_after, places=6)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class TopologyOverlappingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path1 = PathFactory.create(geom=LineString((0, 0), (0, 10)))
        cls.path2 = PathFactory.create(geom=LineString((0, 20), (0, 10)))
        cls.path3 = PathFactory.create(geom=LineString((0, 20), (0, 30)))
        cls.path4 = PathFactory.create(geom=LineString((0, 30), (0, 40)))

        cls.topo1 = TopologyFactory.create(
            paths=[
                (cls.path1, 0.5, 1),
                (cls.path2, 1, 0),
                cls.path3,
                (cls.path4, 0, 0.5),
            ]
        )

        cls.topo2 = TopologyFactory.create(paths=[cls.path2])

        cls.point1 = TopologyFactory.create(paths=[(cls.path2, 0.4, 0.4)])

        cls.point2 = TopologyFactory.create(paths=[(cls.path2, 0.8, 0.8)])

        cls.point3 = TopologyFactory.create(paths=[(cls.path2, 0.6, 0.6)])

    def test_overlapping_returned_can_be_filtered(self):
        overlaps = Topology.overlapping(self.topo1)
        overlaps = overlaps.exclude(pk=self.topo1.pk)
        self.assertEqual(len(overlaps), 4)

        overlaps = Topology.overlapping(self.topo1)
        overlaps = overlaps.filter(pk__in=[self.point1.pk, self.point2.pk])
        self.assertEqual(len(overlaps), 2)

    def test_overlapping_return_sharing_path(self):
        overlaps = Topology.overlapping(self.topo1)
        self.assertTrue(self.topo1 in overlaps)
        self.assertTrue(self.topo2 in overlaps)

    def test_overlapping_sorts_by_order_of_progression(self):
        overlaps = Topology.overlapping(self.topo2)
        self.assertEqual(
            list(overlaps),
            [self.topo2, self.point1, self.point3, self.point2, self.topo1],
        )

    def test_overlapping_sorts_when_path_is_reversed(self):
        overlaps = Topology.overlapping(self.topo1)
        self.assertEqual(
            list(overlaps),
            [self.topo1, self.point2, self.point3, self.point1, self.topo2],
        )

    def test_overlapping_does_not_fail_if_no_records(self):
        from geotrek.trekking.models import Trek

        overlaps = Topology.overlapping(Trek.objects.all())
        self.assertEqual(list(overlaps), [])
