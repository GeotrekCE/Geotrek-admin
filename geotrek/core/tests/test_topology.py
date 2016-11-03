import json
import math

from django.test import TestCase
from django.conf import settings
from django.db import connections, DEFAULT_DB_ALIAS
from django.contrib.gis.geos import Point, LineString

from geotrek.common.utils import dbnow, almostequal
from geotrek.core.factories import (PathFactory, PathAggregationFactory,
                                    TopologyFactory)
from geotrek.core.models import Path, Topology, PathAggregation
from geotrek.core.helpers import TopologyHelper


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


class TopologyTest(TestCase):

    def test_geom_null_is_safe(self):
        t = TopologyFactory.create()
        t.geom = None
        t.save()
        self.assertNotEqual(t.geom, None)

    def test_dates(self):
        t1 = dbnow()
        e = TopologyFactory.build(no_path=True)
        e.save()
        t2 = dbnow()
        self.assertTrue(t1 < e.date_insert < t2)

        e.delete()
        t3 = dbnow()
        self.assertTrue(t2 < e.date_update < t3)

    def test_latestupdate_delete(self):
        for i in range(10):
            TopologyFactory.create()
        t1 = dbnow()
        self.assertTrue(t1 > Topology.objects.latest("date_update").date_update)
        (Topology.objects.all()[0]).delete(force=True)
        self.assertFalse(t1 > Topology.objects.latest("date_update").date_update)

    def test_length(self):
        e = TopologyFactory.build(no_path=True)
        self.assertEqual(e.length, 0)
        e.save()
        self.assertEqual(e.length, 0)
        PathAggregationFactory.create(topo_object=e)
        e.save()
        self.assertNotEqual(e.length, 0)

    def test_kind(self):
        from geotrek.land.models import LandEdge
        from geotrek.land.factories import LandEdgeFactory

        # Test with a concrete inheritance of Topology : LandEdge
        self.assertEqual('TOPOLOGY', Topology.KIND)
        self.assertEqual(0, len(Topology.objects.filter(kind='LANDEDGE')))
        self.assertEqual('LANDEDGE', LandEdge.KIND)
        # Kind of instances
        e = LandEdgeFactory.create()
        self.assertEqual(e.kind, LandEdge.KIND)
        self.assertEqual(1, len(Topology.objects.filter(kind='LANDEDGE')))

    def test_link_closest_visible_path(self):
        """
        Topology must be linked to the closest visible path only
        """
        path_visible = Path(name="visible",
                            geom='LINESTRING(0 0, 1 0, 2 0)',
                            visible=True)
        path_visible.save()
        path_unvisible = Path(name="unvisible",
                              geom='LINESTRING(0 3, 1 3, 2 3)',
                              visible=False)
        path_unvisible.save()

        # default manager see 1 path
        self.assertEqual(Path.objects.count(), 1)

        # custom manager see 2 paths
        self.assertEqual(Path.include_invisible.count(), 2)

        # create topo on visible path
        topology = TopologyHelper._topologypoint(0, 0, None).reload()

        # because FK and M2M are used with default manager only, others tests are in SQL
        conn = connections[DEFAULT_DB_ALIAS]
        cur = conn.cursor()
        cur.execute(
            """
            SELECT t.id as id_path,
                   et.evenement as id_topology,
                   t.visible as visible
            FROM e_r_evenement_troncon et
            JOIN l_t_troncon t ON et.troncon=t.id
            WHERE et.evenement={topo_id}
            """.format(topo_id=topology.pk))

        datas = dictfetchall(cur)

        # topo must be linked to visible path
        self.assertIn(topology.pk, [ele['id_topology'] for ele in datas], u"{}".format(datas))
        self.assertIn(path_visible.pk, [ele['id_path'] for ele in datas], u"{}".format(datas))
        self.assertNotIn(path_unvisible.pk, [ele['id_path'] for ele in datas], u"{}".format(datas))

        # new topo on invible path
        topology = TopologyHelper._topologypoint(0, 3, None).reload()

        cur.execute(
            """
            SELECT t.id as id_path,
                   et.evenement as id_topology,
                   t.visible as visible
            FROM e_r_evenement_troncon et
            JOIN l_t_troncon t ON et.troncon=t.id
            WHERE et.evenement={topo_id}
            """.format(topo_id=topology.pk))

        datas = dictfetchall(cur)

        self.assertIn(topology.pk, [ele['id_topology'] for ele in datas], u"{}".format(datas))
        self.assertIn(path_visible.pk, [ele['id_path'] for ele in datas], u"{}".format(datas))
        self.assertNotIn(path_unvisible.pk, [ele['id_path'] for ele in datas], u"{}".format(datas))
        cur.close()


class TopologyDeletionTest(TestCase):

    def test_deleted_is_hidden_but_still_exists(self):
        topology = TopologyFactory.create(offset=1)
        path = topology.paths.get()
        self.assertEqual(len(PathAggregation.objects.filter(topo_object=topology)), 1)
        self.assertEqual(len(path.topology_set.all()), 1)
        topology.delete()
        # Make sure object remains in database with deleted status
        self.assertEqual(len(PathAggregation.objects.filter(topo_object=topology)), 1)
        # Make sure object has deleted status
        self.assertTrue(topology.deleted)
        # Make sure object still exists
        self.assertEqual(len(path.topology_set.all()), 1)
        self.assertIn(topology, Topology.objects.all())
        # Make sure object can be hidden from managers
        self.assertNotIn(topology, Topology.objects.existing())
        self.assertEqual(len(path.topology_set.existing()), 0)

    def test_deleted_when_all_path_are_deleted(self):
        topology = TopologyFactory.create()
        self.assertFalse(topology.deleted)

        paths = path = topology.paths.all()
        for path in paths:
            path.delete()

        topology.reload()
        self.assertTrue(topology.deleted)


class TopologyMutateTest(TestCase):

    def test_mutate(self):
        topology1 = TopologyFactory.create(no_path=True)
        self.assertEqual(len(topology1.paths.all()), 0)
        topology2 = TopologyFactory.create(offset=14.5)
        self.assertEqual(len(topology2.paths.all()), 1)
        # Normal usecase
        topology1.mutate(topology2)
        self.assertEqual(topology1.offset, 14.5)
        self.assertEqual(len(topology1.paths.all()), 1)
        # topology2 does not exist anymore
        self.assertEqual(len(Topology.objects.filter(pk=topology2.pk)), 0)
        # Without deletion
        topology3 = TopologyFactory.create()
        topology1.mutate(topology3, delete=False)
        # topology3 still exists
        self.assertEqual(len(Topology.objects.filter(pk=topology3.pk)), 1)

    def test_mutate_intersection(self):
        # Mutate a Point topology at an intersection, and make sure its aggregations
        # are not duplicated (c.f. SQL triggers)

        # Create a 3 paths intersection
        PathFactory.create(geom=LineString((0, 0), (1, 0)))
        p2 = PathFactory.create(geom=LineString((1, 0), (2, 0)))
        PathFactory.create(geom=LineString((1, 0), (1, 1)))
        # Create a topology point at this intersection
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(p2, start=0.0, end=0.0)
        self.assertTrue(topology.ispoint())
        # Make sure, the trigger worked, and linked to 3 paths
        self.assertEqual(len(topology.paths.all()), 3)
        # Mutate it to another one !
        topology2 = TopologyFactory.create(no_path=True)
        self.assertEqual(len(topology2.paths.all()), 0)
        self.assertTrue(topology2.ispoint())
        topology2.mutate(topology)
        self.assertEqual(len(topology2.paths.all()), 3)


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
        self.assertTrue(almostequal(0.5, position))
        self.assertTrue(almostequal(-1.414, distance))
        # Verify that deserializing this, we obtain the same original coordinates
        # (use lat/lng as in forms)
        poi.transform(settings.API_SRID)
        poitopo = Topology.deserialize({'lat': poi.y, 'lng': poi.x})
        # Computed topology properties match original interpolation
        self.assertTrue(almostequal(0.5, poitopo.aggregations.all()[0].start_position))
        self.assertTrue(almostequal(-1.414, poitopo.offset))
        # Resulting geometry
        self.assertTrue(almostequal(3, poitopo.geom.x))
        self.assertTrue(almostequal(1, poitopo.geom.y))

    def test_point_geom_not_moving(self):
        """
        Modify path, point not moving
        +                  +
        |                  |
         \     X          /        X
         /                \
        |                  |
        +                  +
        """
        p1 = PathFactory.create(geom=LineString((0, 0),
                                                (0, 5),
                                                (5, 10),
                                                (0, 15),
                                                (0, 20)))
        poi = Point(10, 10, srid=settings.SRID)
        poi.transform(settings.API_SRID)
        poitopo = Topology.deserialize({'lat': poi.y, 'lng': poi.x})
        self.assertEqual(0.5, poitopo.aggregations.all()[0].start_position)
        self.assertTrue(almostequal(-5, poitopo.offset))
        # It should have kept its position !
        self.assertTrue(almostequal(10, poitopo.geom.x))
        self.assertTrue(almostequal(10, poitopo.geom.y))
        # Change path, it should still be in the same position
        p1.geom = LineString((0, 0),
                             (0, 5),
                             (-5, 10),
                             (0, 15),
                             (0, 20))
        p1.save()
        poitopo.reload()
        self.assertTrue(almostequal(10, poitopo.geom.x))
        self.assertTrue(almostequal(10, poitopo.geom.y))

    def test_point_offset_kept(self):
        """
        Shorten path, offset kept.

          X                        X
        +-----------+            +------+

        """
        p1 = PathFactory.create(geom=LineString((0, 0), (20, 0)))
        poi = Point(5, 10, srid=settings.SRID)
        poi.transform(settings.API_SRID)
        poitopo = Topology.deserialize({'lat': poi.y, 'lng': poi.x})
        self.assertTrue(almostequal(0.25, poitopo.aggregations.all()[0].start_position))
        self.assertTrue(almostequal(10, poitopo.offset))

        p1.geom = LineString((0, 0), (10, 0))
        p1.save()
        poitopo.reload()

        self.assertTrue(almostequal(10, poitopo.offset))
        # Not moved:
        self.assertTrue(almostequal(5, poitopo.geom.x))
        self.assertTrue(almostequal(10, poitopo.geom.y))

    def test_point_offset_updated(self):
        """
        Shorten path, offset updated.

               X                              X
        +-----------+            +------+

        """
        p1 = PathFactory.create(geom=LineString((0, 0), (20, 0)))
        poi = Point(10, 10, srid=settings.SRID)
        poi.transform(settings.API_SRID)
        poitopo = Topology.deserialize({'lat': poi.y, 'lng': poi.x})
        self.assertTrue(almostequal(0.5, poitopo.aggregations.all()[0].start_position))
        self.assertTrue(almostequal(10, poitopo.offset))

        p1.geom = LineString((0, 0), (0, 5))
        p1.save()
        poitopo.reload()
        self.assertTrue(almostequal(11.180339887, poitopo.offset))
        # Not moved:
        self.assertTrue(almostequal(10, poitopo.geom.x))
        self.assertTrue(almostequal(10, poitopo.geom.y))

    def test_point_geom_moving(self):
        p1 = PathFactory.create(geom=LineString((0, 0),
                                                (0, 5)))
        poi = Point(0, 2.5, srid=settings.SRID)
        poi.transform(settings.API_SRID)
        poitopo = Topology.deserialize({'lat': poi.y, 'lng': poi.x})
        self.assertTrue(almostequal(0.5, poitopo.aggregations.all()[0].start_position))
        self.assertTrue(almostequal(0, poitopo.offset))
        self.assertTrue(almostequal(0, poitopo.geom.x))
        self.assertTrue(almostequal(2.5, poitopo.geom.y))
        p1.geom = LineString((10, 0),
                             (10, 5))
        p1.save()
        poitopo.reload()
        self.assertTrue(almostequal(10, poitopo.geom.x))
        self.assertTrue(almostequal(2.5, poitopo.geom.y))

    def test_junction_point(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (2, 2)))
        p2 = PathFactory.create(geom=LineString((0, 0), (2, 0)))
        p3 = PathFactory.create(geom=LineString((0, 2), (0, 0)))

        # Create a junction point topology
        t = TopologyFactory.create(no_path=True)
        self.assertEqual(len(t.paths.all()), 0)

        pa = PathAggregationFactory.create(topo_object=t, path=p1,
                                           start_position=0.0, end_position=0.0)

        self.assertItemsEqual(t.paths.all(), [p1, p2, p3])

        # Update to a non junction point topology
        pa.end_position = 0.4
        pa.save()

        self.assertItemsEqual(t.paths.all(), [p1])

        # Update to a junction point topology
        pa.end_position = 0.0
        pa.save()

        self.assertItemsEqual(t.paths.all(), [p1, p2, p3])

    def test_point_at_end_of_path_not_moving_after_mutate(self):
        PathFactory.create(geom=LineString((400, 400), (410, 400),
                                           srid=settings.SRID))
        self.assertEqual(1, len(Path.objects.all()))

        father = Topology.deserialize({'lat': -1, 'lng': -1})

        poi = Point(500, 600, srid=settings.SRID)
        poi.transform(settings.API_SRID)
        son = Topology.deserialize({'lat': poi.y, 'lng': poi.x})
        father.mutate(son)
        self.assertTrue(almostequal(father.geom.x, 500))
        self.assertTrue(almostequal(father.geom.y, 600))


class TopologyLineTest(TestCase):

    def test_topology_geom(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (2, 2)))
        p2 = PathFactory.create(geom=LineString((2, 2), (2, 0)))
        p3 = PathFactory.create(geom=LineString((2, 0), (4, 0)))

        # Type Point
        t = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t, path=p1,
                                      start_position=0.5, end_position=0.5)
        t = Topology.objects.get(pk=t.pk)
        self.assertEqual(t.geom, Point((1, 1)))

        # 50% of path p1, 100% of path p2
        t = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t, path=p1,
                                      start_position=0.5)
        PathAggregationFactory.create(topo_object=t, path=p2)
        t = Topology.objects.get(pk=t.pk)
        self.assertEqual(t.geom, LineString((1, 1), (2, 2), (2, 0)))

        # 100% of path p2 and p3, with offset of 1
        t = TopologyFactory.create(no_path=True, offset=1)
        PathAggregationFactory.create(topo_object=t, path=p2)
        PathAggregationFactory.create(topo_object=t, path=p3)
        t.save()
        self.assertEqual(t.geom, LineString((3, 2), (3, 1), (4, 1)))

        # Change offset, geometry is computed again
        t.offset = 0.5
        t.save()
        self.assertEqual(t.geom, LineString((2.5, 2), (2.5, 0.5), (4, 0.5)))

    def test_topology_geom_should_not_be_sampled(self):
        coords = [(x, math.sin(x)) for x in range(100)]
        sampled_3d = [(x, math.sin(x), math.cos(x)) for x in range(0, 100, 5)]
        p1 = PathFactory.create(geom=LineString(*coords))
        p1.geom_3d = LineString(*sampled_3d)
        p1.save(update_fields=['geom_3d'])

        t = TopologyFactory.create(no_path=True)
        t.add_path(p1, start=0.0, end=1.0)
        t.save()

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
        t = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t, path=p1)
        PathAggregationFactory.create(topo_object=t, path=p3)
        PathAggregationFactory.create(topo_object=t, path=p3,
                                      start_position=0.5, end_position=0.5)
        PathAggregationFactory.create(topo_object=t, path=p4)
        t.save()
        self.assertEqual(t.geom, LineString((0, 0), (2, 0), (4, 0), (6, 0)))
        """
        From p1 to p4, through p2
        """
        t = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t, path=p1)
        PathAggregationFactory.create(topo_object=t, path=p2)
        # There will a forced passage in database...
        PathAggregationFactory.create(topo_object=t, path=p2,
                                      start_position=0.5, end_position=0.5)
        PathAggregationFactory.create(topo_object=t, path=p4)
        t.save()
        self.assertEqual(t.geom, LineString((0, 0), (2, 0), (2, 1), (4, 1), (4, 0), (6, 0)))

        """
        From p1 to p4, though p2, but **with start/end at 0.0**
        """
        t2 = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t2, path=p1)
        PathAggregationFactory.create(topo_object=t2, path=p2)
        PathAggregationFactory.create(topo_object=t2, path=p2,
                                      start_position=0.0, end_position=0.0)
        PathAggregationFactory.create(topo_object=t2, path=p4)
        t2.save()
        self.assertEqual(t2.geom, t.geom)

    def test_troncon_geom_update(self):
        # Create a path
        p = PathFactory.create(geom=LineString((0, 0), (4, 0)))

        # Create a linear topology
        t1 = TopologyFactory.create(offset=1, no_path=True)
        t1.add_path(p, start=0.0, end=0.5)
        t1_agg = t1.aggregations.get()

        # Create a point topology
        t2 = TopologyFactory.create(offset=-1, no_path=True)
        t2.add_path(p, start=0.5, end=0.5)
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


class TopologyCornerCases(TestCase):
    def test_opposite_paths(self):
        """
                A  C
        B +-------+-------+ D

        """
        ab = PathFactory.create(geom=LineString((5, 0), (0, 0)))
        cd = PathFactory.create(geom=LineString((5, 0), (10, 0)))
        topo = TopologyFactory.create(no_path=True)
        topo.add_path(ab, start=0.2, end=0)
        topo.add_path(cd, start=0, end=0.2)
        topo.save()
        expected = LineString((4, 0), (5, 0), (6, 0))
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
        topo = TopologyFactory.create(no_path=True)
        topo.add_path(ab, start=0.2, end=0)
        topo.add_path(ac)
        topo.add_path(cd, start=0, end=0.2)
        topo.save()
        expected = LineString((4, 0), (5, 0), (10, 0), (11, 0))
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
        topo = TopologyFactory.create(no_path=True)
        topo.add_path(p1, start=0.5, end=1)
        topo.add_path(p2, start=0, end=0.8)
        topo.add_path(p2, start=0.8, end=0.8)
        topo.add_path(p2, start=0.8, end=0)
        topo.add_path(p3, start=0, end=0.5)
        topo.save()
        self.assertEqual(topo.geom, LineString((2.5, 0), (5, 0), (5, 10),
                                               (7, 10), (5, 10), (5, 0),
                                               (7.5, 0)))

    def test_return_path_serialized(self):
        """
        Same as test_return_path() but from deserialization.
        """
        p1 = PathFactory.create(geom=LineString((0, 0), (10, 0)))
        p2 = PathFactory.create(geom=LineString((5, 0), (5, 10), (10, 10)))
        p3 = Path.objects.filter(name=p1.name).exclude(pk=p1.pk)[0]  # Was splitted :)
        topo = Topology.deserialize("""
           [{"offset":0,
             "positions":{"0":[0.5,1],
                          "1":[0.0, 0.8]},
             "paths":[%(p1)s,%(p2)s]
            },
            {"offset":0,
             "positions":{"0":[0.8,0.0],
                          "1":[0.0, 0.5]},
             "paths":[%(p2)s,%(p3)s]
            }
           ]
        """ % {'p1': p1.pk, 'p2': p2.pk, 'p3': p3.pk})
        topo.save()
        self.assertEqual(topo.geom, LineString((2.5, 0), (5, 0), (5, 10),
                                               (7, 10), (5, 10), (5, 0),
                                               (7.5, 0)))


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
        topo = TopologyFactory.create(no_path=True)
        topo.add_path(p1)
        topo.add_path(p2)
        topo.save()
        self.assertEqual(topo.geom, LineString((10, 0), (0, 0), (0, 5), (10, 5), (10, 0)))
        # Subpart, like in diagram
        topo = TopologyFactory.create(no_path=True)
        topo.add_path(p1, start=0.8, end=1)
        topo.add_path(p2)
        topo.add_path(p1, start=0, end=0.2)
        topo.save()
        self.assertEqual(topo.geom, LineString((2, 0), (0, 0), (0, 5),
                                               (10, 5), (10, 0), (8, 0)))

    def test_trek_loop(self):
        """
                            =========
                           ||       ||
        +-------===========+=========+----------+
        """
        p1 = PathFactory.create(geom=LineString((0, 0), (10, 0)))
        p2 = PathFactory.create(geom=LineString((10, 0), (30, 0)))
        p3 = PathFactory.create(geom=LineString((10, 0), (10, 5),
                                                (20, 5), (20, 0)))
        topo = TopologyFactory.create(no_path=True)
        topo.add_path(p1, start=0.3, end=1)
        topo.add_path(p3)
        topo.add_path(p2, start=1, end=0)
        topo.add_path(p1, start=1, end=0.3)
        topo.save()
        self.assertEqual(topo.geom, LineString((3, 0), (10, 0), (10, 5), (20, 5), (20, 0),
                                               (10, 0), (3, 0)))

    def test_spoon_loop(self):
        """
                            =====<====
                           ||       ||
        +-------===<===>===+=====>===
        """
        p1 = PathFactory.create(geom=LineString((0, 0), (10, 0)))
        p2 = PathFactory.create(geom=LineString((10, 0), (10, 5),
                                                (20, 5), (20, 0),
                                                (10, 0)))
        topo = TopologyFactory.create(no_path=True)
        topo.add_path(p1, start=0.3, end=1)
        topo.add_path(p2, start=1, end=0.4)
        topo.add_path(p2, start=0.4, end=0.4)
        topo.add_path(p2, start=0.4, end=0.2)
        topo.add_path(p2, start=0.2, end=0.2)
        topo.add_path(p2, start=0.2, end=0)
        topo.add_path(p1, start=1, end=0.3)
        topo.save()
        self.assertEqual(topo.geom, LineString((3, 0), (10, 0), (20, 0), (20, 5),
                                               (17, 5), (11, 5),  # extra point due middle aggregation
                                               (10, 5), (10, 0), (3, 0)))

        # Deserializing should work too
        topod = Topology.deserialize("""
           [{"positions":{"0":[0.3,1],"1":[1, 0.4]},"paths":[%(pk1)s,%(pk2)s]},
            {"positions":{"0":[0.4, 0.2]},"paths":[%(pk2)s]},
            {"positions":{"0":[0.2,0],"1":[1,0.3]},"paths":[%(pk2)s,%(pk1)s]}]""" % {'pk1': p1.pk, 'pk2': p2.pk})
        self.assertEqual(topo.geom, topod.geom)
        self.assertEqual(len(topod.aggregations.all()), 7)

    def test_spoon_loop_2(self):
        """
                            =====>====
                           ||       ||
        +-------===<===>===+=====<===
        """
        p1 = PathFactory.create(geom=LineString((0, 0), (10, 0)))
        p2 = PathFactory.create(geom=LineString((10, 0), (10, 5),
                                                (20, 5), (20, 0),
                                                (10, 0)))
        topo = TopologyFactory.create(no_path=True)
        topo.add_path(p1, start=0.3, end=1, order=1)
        topo.add_path(p2, start=0, end=0.4, order=2)
        topo.add_path(p2, start=0.4, end=0.4, order=3)
        topo.add_path(p2, start=0.4, end=0.8, order=4)
        topo.add_path(p2, start=0.8, end=0.8, order=5)
        topo.add_path(p2, start=0.8, end=1.0, order=6)
        topo.add_path(p1, start=1, end=0.3, order=7)
        topo.save()
        self.assertEqual(topo.geom, LineString((3, 0), (10, 0), (10, 5),
                                               (17, 5), (20, 5),  # extra point due middle aggregation
                                               (20, 0), (16, 0), (10, 0), (3, 0)))

        # De/Serializing should work too
        serialized = """
           [{"kind": "TOPOLOGY","positions":{"0":[0.3,1],"1":[0, 0.4]},"paths":[%(pk1)s,%(pk2)s],"offset": 0.0,"pk": %(topo)s},
            {"kind": "TOPOLOGY","positions":{"0":[0.4, 0.8]},"paths":[%(pk2)s],"offset": 0.0,"pk": %(topo)s},
            {"kind": "TOPOLOGY","positions":{"0":[0.8,1],"1":[1,0.3]},"paths":[%(pk2)s,%(pk1)s],"offset": 0.0,"pk": %(topo)s}]""" % {
            'topo': topo.pk,
            'pk1': p1.pk,
            'pk2': p2.pk
        }

        self.assertEqual(json.loads(serialized), json.loads(topo.serialize()))
        topod = Topology.deserialize(serialized)
        self.assertEqual(topo.geom, topod.geom)
        self.assertEqual(len(topod.aggregations.all()), 7)

    def test_trek_all_reverse(self):
        """

        +----<===+=======+====|----->

        """
        p1 = PathFactory.create(geom=LineString((0, 0), (10, 0)))
        p2 = PathFactory.create(geom=LineString((10, 0), (20, 0)))
        p3 = PathFactory.create(geom=LineString((20, 0), (30, 0)))

        topo = TopologyFactory.create(no_path=True)
        topo.add_path(p3, start=0.2, end=0)
        topo.add_path(p2, start=1, end=0)
        topo.add_path(p1, start=1, end=0.9)
        topo.save()
        self.assertEqual(topo.geom, LineString((22.0, 0.0), (20.0, 0.0), (10.0, 0.0), (9.0, 0.0)))


class TopologySerialization(TestCase):

    def test_serialize_line(self):
        path = PathFactory.create()
        test_objdict = {u'kind': Topology.KIND,
                        u'offset': 1.0,
                        u'positions': {},
                        u'paths': [path.pk]}
        # +|========>+
        topo = TopologyFactory.create(offset=1.0, no_path=True)
        topo.add_path(path)
        test_objdict['pk'] = topo.pk
        test_objdict['positions']['0'] = [0.0, 1.0]
        objdict = json.loads(topo.serialize())
        self.assertDictEqual(objdict[0], test_objdict)

        # +<========|+
        topo = TopologyFactory.create(offset=1.0, no_path=True)
        topo.add_path(path, start=1.0, end=0.0)
        test_objdict['pk'] = topo.pk
        test_objdict['positions']['0'] = [1.0, 0.0]
        objdict = json.loads(topo.serialize())
        self.assertDictEqual(objdict[0], test_objdict)

        # +|========>+<========|+
        path2 = PathFactory.create()
        topo = TopologyFactory.create(offset=1.0, no_path=True)
        topo.add_path(path, start=0.0, end=1.0)
        topo.add_path(path2, start=1.0, end=0.0)
        test_objdict['pk'] = topo.pk
        test_objdict['paths'] = [path.pk, path2.pk]
        test_objdict['positions'] = {'0': [0.0, 1.0], '1': [1.0, 0.0]}
        objdict = json.loads(topo.serialize())
        self.assertDictEqual(objdict[0], test_objdict)

        # +<========|+|========>+
        topo = TopologyFactory.create(offset=1.0, no_path=True)
        topo.add_path(path, start=1.0, end=0.0)
        topo.add_path(path2, start=0.0, end=1.0)
        test_objdict['pk'] = topo.pk
        test_objdict['paths'] = [path.pk, path2.pk]
        test_objdict['positions'] = {'0': [1.0, 0.0], '1': [0.0, 1.0]}
        objdict = json.loads(topo.serialize())
        self.assertDictEqual(objdict[0], test_objdict)

    def test_serialize_point(self):
        path = PathFactory.create()
        topology = TopologyFactory.create(offset=1, no_path=True)
        topology.add_path(path, start=0.5, end=0.5)
        fieldvalue = topology.serialize()
        # fieldvalue is like '{"lat": -5.983842291017086, "lng": -1.3630770374505987, "kind": "TOPOLOGY"}'
        field = json.loads(fieldvalue)
        self.assertEqual(field['pk'], topology.pk)
        self.assertAlmostEqual(field['lat'], 46.5004566)
        self.assertAlmostEqual(field['lng'], 3.0006428)
        self.assertEqual(field['kind'], "TOPOLOGY")

    def test_serialize_two_consecutive_forced(self):
        path1 = PathFactory.create()
        path2 = PathFactory.create()
        path3 = PathFactory.create()
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(path1)
        topology.add_path(path2, start=0.2, end=0.2)
        topology.add_path(path2, start=0.4, end=0.4)
        topology.add_path(path3)
        fieldvalue = topology.serialize()
        field = json.loads(fieldvalue)
        self.assertEqual(len(field), 2)


class TopologyDerialization(TestCase):

    def test_deserialize_foreignkey(self):
        topology = TopologyFactory.create(offset=1, no_path=True)
        deserialized = Topology.deserialize(topology.pk)
        self.assertEqual(topology, deserialized)

    def test_deserialize_unedited_point_topology(self):
        topology = TopologyFactory.create(offset=1, no_path=True)
        deserialized = Topology.deserialize({'pk': topology.pk})
        self.assertEqual(topology, deserialized)

    def test_deserialize_unedited_line_topology(self):
        topology = TopologyFactory.create(offset=1, no_path=True)
        deserialized = Topology.deserialize([{'pk': topology.pk}, {}])
        self.assertEqual(topology, deserialized)

    def test_deserialize_line(self):
        path = PathFactory.create()
        topology = Topology.deserialize('[{"paths": [%s], "positions": {"0": [0.0, 1.0]}, "offset": 1}]' % (path.pk))
        self.assertEqual(topology.offset, 1)
        self.assertEqual(topology.kind, Topology.KIND)
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(topology.aggregations.all()[0].path, path)
        self.assertEqual(topology.aggregations.all()[0].start_position, 0.0)
        self.assertEqual(topology.aggregations.all()[0].end_position, 1.0)

    def test_deserialize_multiple_lines(self):
        # Multiple paths
        p1 = PathFactory.create(geom=LineString((0, 0), (2, 2)))
        p2 = PathFactory.create(geom=LineString((2, 2), (2, 0)))
        p3 = PathFactory.create(geom=LineString((2, 0), (4, 0)))
        pks = [p.pk for p in [p1, p2, p3]]
        topology = Topology.deserialize('{"paths": %s, "positions": {"0": [0.0, 1.0], "2": [0.0, 1.0]}, "offset": 1}' % (pks))
        for i in range(3):
            self.assertEqual(topology.aggregations.all()[i].start_position, 0.0)
            self.assertEqual(topology.aggregations.all()[i].end_position, 1.0)

        topology = Topology.deserialize('{"paths": %s, "positions": {"0": [0.3, 1.0], "2": [0.0, 0.7]}, "offset": 1}' % (pks))
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
        topology = Topology.deserialize('{"lng": %s, "lat": %s}' % (p.x, p.y))
        self.assertAlmostEqual(topology.offset, -70.7106781)
        self.assertEqual(len(topology.paths.all()), 1)
        pagg = topology.aggregations.get()
        self.assertTrue(almostequal(pagg.start_position, 0.5))
        self.assertTrue(almostequal(pagg.end_position, 0.5))

    def test_deserialize_serialize(self):
        path = PathFactory.create(geom=LineString((1, 1), (2, 2), (2, 0)))
        before = TopologyFactory.create(offset=1, no_path=True)
        before.add_path(path, start=0.5, end=0.5)

        # Deserialize its serialized version !
        after = Topology.deserialize(before.serialize())

        self.assertEqual(len(before.paths.all()), len(after.paths.all()))
        start_before = before.aggregations.all()[0].start_position
        end_before = before.aggregations.all()[0].end_position
        start_after = after.aggregations.all()[0].start_position
        end_after = after.aggregations.all()[0].end_position
        self.assertTrue(almostequal(start_before, start_after), '%s != %s' % (start_before, start_after))
        self.assertTrue(almostequal(end_before, end_after), '%s != %s' % (end_before, end_after))


class TopologyOverlappingTest(TestCase):

    def setUp(self):
        self.path1 = PathFactory.create(geom=LineString((0, 0), (0, 10)))
        self.path2 = PathFactory.create(geom=LineString((0, 20), (0, 10)))
        self.path3 = PathFactory.create(geom=LineString((0, 20), (0, 30)))
        self.path4 = PathFactory.create(geom=LineString((0, 30), (0, 40)))

        self.topo1 = TopologyFactory.create(no_path=True)
        self.topo1.add_path(self.path1, start=0.5, end=1)
        self.topo1.add_path(self.path2, start=1, end=0)
        self.topo1.add_path(self.path3)
        self.topo1.add_path(self.path4, start=0, end=0.5)

        self.topo2 = TopologyFactory.create(no_path=True)
        self.topo2.add_path(self.path2)

        self.point1 = TopologyFactory.create(no_path=True)
        self.point1.add_path(self.path2, start=0.4, end=0.4)

        self.point2 = TopologyFactory.create(no_path=True)
        self.point2.add_path(self.path2, start=0.8, end=0.8)

        self.point3 = TopologyFactory.create(no_path=True)
        self.point3.add_path(self.path2, start=0.6, end=0.6)

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
        self.assertEqual(list(overlaps), [self.topo2,
                                          self.point1, self.point3, self.point2, self.topo1])

    def test_overlapping_sorts_when_path_is_reversed(self):
        overlaps = Topology.overlapping(self.topo1)
        self.assertEqual(list(overlaps), [self.topo1,
                                          self.point2, self.point3, self.point1, self.topo2])

    def test_overlapping_does_not_fail_if_no_records(self):
        from geotrek.trekking.models import Trek
        overlaps = Topology.overlapping(Trek.objects.all())
        self.assertEqual(list(overlaps), [])
