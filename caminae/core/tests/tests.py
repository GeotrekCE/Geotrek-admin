from django.test import TestCase
from django.conf import settings
from django.utils import simplejson
from django.contrib.gis.geos import Point, LineString
from django.db import connections, DEFAULT_DB_ALIAS, IntegrityError

from caminae.mapentity.tests import MapEntityTest
from caminae.common.utils import dbnow, almostequal
from caminae.authent.factories import UserFactory, PathManagerFactory, StructureFactory
from caminae.authent.models import Structure, default_structure
from caminae.core.factories import (PathFactory, PathAggregationFactory, 
    TopologyFactory, StakeFactory, TrailFactory, ComfortFactory)
from caminae.core.models import Path, Topology, PathAggregation


class ViewsTest(MapEntityTest):
    model = Path
    modelfactory = PathFactory
    userfactory = PathManagerFactory

    def get_bad_data(self):
        return {'geom': 'argh !'}, u'Acune valeur g\xe9om\xe9trique fournie.'

    def get_good_data(self):
        return {
            'name': '',
            'structure': default_structure().pk,
            'stake': '',
            'comfort': ComfortFactory.create().pk,
            'trail': '',
            'comments': '',
            'departure': '',
            'arrival': '',
            'datasource': '',
            'valid': 'on',
            'geom': 'LINESTRING (0.0 0.0 0.0, 1.0 1.0 1.0)',
        }

    def test_structurerelated_filter(self):
        def test_structure(structure, stake):
            user = self.userfactory(password='booh')
            p = user.profile
            p.structure = structure
            p.save()
            success = self.client.login(username=user.username, password='booh')
            self.assertTrue(success)
            response = self.client.get(Path.get_add_url())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('form' in response.context)
            form = response.context['form']
            self.assertTrue('stake' in form.fields)
            stakefield = form.fields['stake']
            self.assertTrue((stake.pk, unicode(stake)) in stakefield.choices)
            self.client.logout()
        # Test for two structures
        s1 = StructureFactory.create()
        s2 = StructureFactory.create()
        st1 = StakeFactory.create(structure=s1)
        StakeFactory.create(structure=s1)
        st2 = StakeFactory.create(structure=s2)
        StakeFactory.create(structure=s2)
        test_structure(s1, st1)
        test_structure(s2, st2)


# FIXME: this test has random results (as reported by Hudson)
#class StakeTest(TestCase):
#    def test_comparison(self):
#        low = StakeFactory.create()
#        high = StakeFactory.create()
#        # In case SERIAL field was reinitialized
#        if high.pk < low.pk:
#            tmp = high
#            high = low
#            low = tmp
#            self.assertTrue(low.pk < high.pk)
#        self.assertTrue(low < high)
#        self.assertTrue(low <= high)
#        self.assertFalse(low > high)
#        self.assertFalse(low >= high)
#        self.assertFalse(low == high)


class PathTest(TestCase):
    def test_paths_bystructure(self):
        user = UserFactory()
        p1 = PathFactory()
        p2 = PathFactory(structure=Structure.objects.create(name="other"))

        self.assertEqual(user.profile.structure, p1.structure)
        self.assertNotEqual(user.profile.structure, p2.structure)

        self.assertEqual(len(Structure.objects.all()), 2)
        self.assertEqual(len(Path.objects.all()), 2)

        self.assertEqual(Path.in_structure.for_user(user)[0], Path.for_user(user)[0])
        self.assertTrue(p1 in Path.in_structure.for_user(user))
        self.assertFalse(p2 in Path.in_structure.for_user(user))

        # Change user structure on-the-fly
        profile = user.profile
        profile.structure = p2.structure
        profile.save()

        self.assertEqual(user.profile.structure.name, "other")
        self.assertFalse(p1 in Path.in_structure.for_user(user))
        self.assertTrue(p2 in Path.in_structure.for_user(user))

    def test_dates(self):
        t1 = dbnow()
        p = PathFactory()
        t2 = dbnow()
        self.assertTrue(t1 < p.date_insert < t2,
                        msg='Date interval failed: %s < %s < %s' % (
                            t1, p.date_insert, t2
                        ))

        p.name = "Foo"
        p.save()
        t3 = dbnow()
        self.assertTrue(t2 < p.date_update < t3,
                        msg='Date interval failed: %s < %s < %s' % (
                            t2, p.date_update, t3
                       ))

    def test_elevation(self):
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
        self.assertEqual(len(profile), 3)
        self.assertEqual(profile[0][0], 0.0)
        self.assertEqual(profile[0][1], 4)
        self.assertTrue(1.4 < profile[1][0] < 1.5)
        self.assertEqual(profile[1][1], 5)
        self.assertTrue(3.8 < profile[2][0] < 3.9)
        self.assertEqual(profile[2][1], 3)

    def test_length(self):
        p = PathFactory.build()
        self.assertEqual(p.length, 0)
        p.save()
        self.assertNotEqual(p.length, 0)

    def test_delete_cascade(self):
        from caminae.trekking.models import Trek
        from caminae.trekking.factories import TrekFactory

        p1 = PathFactory.create()
        p2 = PathFactory.create()
        t = TrekFactory.create(no_path=True)
        t.add_path(p1)
        t.add_path(p2)

        # Everything should be all right before delete
        self.assertTrue(t.published)
        self.assertFalse(t.deleted)
        self.assertEqual(t.aggregations.count(), 2)

        # When a path is deleted
        p1.delete()
        t = Trek.objects.get(pk=t.pk)
        self.assertFalse(t.published)
        self.assertFalse(t.deleted)
        self.assertEqual(t.aggregations.count(), 1)

        # Reset published status
        t.published = True
        t.save()

        # When all paths are deleted
        p2.delete()
        t = Trek.objects.get(pk=t.pk)
        self.assertFalse(t.published)
        self.assertTrue(t.deleted)
        self.assertEqual(t.aggregations.count(), 0)

    def test_geom_update(self):
        # Create a path
        p = PathFactory.create(geom=LineString((0,0,0),(4,0,0)))

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
        self.assertEqual(t1.geom.coords, ((0,1,0),(2,1,0)))
        self.assertEqual(t1_agg.start_position, 0.0)
        self.assertEqual(t1_agg.end_position, 0.5)

        # Ensure point topology is correct before path modification
        self.assertEqual(t2.offset, -1)
        self.assertEqual(t2.geom.coords, (2,-1,0))
        self.assertEqual(t2_agg.start_position, 0.5)
        self.assertEqual(t2_agg.end_position, 0.5)

        # Modify path geometry and refresh computed data
        p.geom = LineString((0,2,0),(8,2,0))
        p.save()
        t1.reload()
        t1_agg = t1.aggregations.get()
        t2.reload()
        t2_agg = t2.aggregations.get()

        # Ensure linear topology is correct after path modification
        self.assertEqual(t1.offset, 1)
        self.assertEqual(t1.geom.coords, ((0,3,0),(4,3,0)))
        self.assertEqual(t1_agg.start_position, 0.0)
        self.assertEqual(t1_agg.end_position, 0.5)

        # Ensure point topology is correct before path modification
        self.assertEqual(t2.offset, -3)
        self.assertEqual(t2.geom.coords, (2,-1,0))
        self.assertEqual(t2_agg.start_position, 0.25)
        self.assertEqual(t2_agg.end_position, 0.25)

    def test_valid_geometry(self):
        connection = connections[DEFAULT_DB_ALIAS]

        # Create path with self-intersection
        p = PathFactory.build(geom=LineString((0,0,0),(2,0,0),(1,1,0),(1,-1,0)))
        self.assertRaises(IntegrityError, p.save)
        # FIXME: Why a regular transaction.rollback does not work???
        connection.close() # Clear DB exception at psycopg level

        # Fix self-intersection
        p.geom = LineString((0,0,0),(2,0,0),(1,1,0))
        p.save()

        # Update with self-intersection
        p.geom = LineString((0,0,0),(2,0,0),(1,1,0),(1,-1,0))
        self.assertRaises(IntegrityError, p.save)
        connection.close() # Clear DB exception at psycopg level


class TopologyTest(TestCase):
    def test_dates(self):
        t1 = dbnow()
        e = TopologyFactory.build(no_path=True)
        e.save()
        t2 = dbnow()
        self.assertTrue(t1 < e.date_insert < t2)

        e.delete()
        t3 = dbnow()
        self.assertTrue(t2 < e.date_update < t3)

    def test_length(self):
        e = TopologyFactory.build(no_path=True)
        self.assertEqual(e.length, 0)
        e.save()
        self.assertEqual(e.length, 0)
        PathAggregationFactory.create(topo_object=e)
        e.save()
        self.assertNotEqual(e.length, 0)

    def test_kind(self):
        from caminae.land.models import LandEdge
        from caminae.land.factories import LandEdgeFactory

        # Test with a concrete inheritance of Topology : LandEdge
        self.assertEqual('TOPOLOGY', Topology.KIND)
        self.assertEqual(0, len(Topology.objects.filter(kind='LANDEDGE')))
        self.assertEqual('LANDEDGE', LandEdge.KIND)
        # Kind of instances
        e = LandEdgeFactory.create()
        self.assertEqual(e.kind, LandEdge.KIND)
        self.assertEqual(1, len(Topology.objects.filter(kind='LANDEDGE')))

    def test_delete(self):
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
        self.assertTrue(topology2.deleted)
        # Without deletion
        topology3 = TopologyFactory.create()
        topology1.mutate(topology3, delete=False)
        # topology3 still exists
        self.assertEqual(len(Topology.objects.filter(pk=topology3.pk)), 1)

    def test_mutate_intersection(self):
        # Mutate a Point topology at an intersection, and make sure its aggregations
        # are not duplicated (c.f. SQL triggers)
        
        # Create a 3 paths intersection
        p1 = PathFactory.create(geom=LineString((0,0,0), (1,0,0)))
        p2 = PathFactory.create(geom=LineString((1,0,0), (2,0,0)))
        p3 = PathFactory.create(geom=LineString((1,0,0), (1,1,0)))
        # Create a topology point at this intersection
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(p2, start=0.0, end=0.0)
        # Make sure, the trigger worked, and linked to 3 paths
        self.assertEqual(len(topology.paths.all()), 3)
        # Mutate it to another one !
        topology2 = TopologyFactory.create(no_path=True)
        self.assertEqual(len(topology2.paths.all()), 0)
        topology2.mutate(topology)
        self.assertEqual(len(topology2.paths.all()), 3)

    def test_serialize(self):
        # At least two path are required
        t = TopologyFactory.create(offset=1)
        self.assertEqual(len(t.paths.all()), 1)

        # This path as been created automatically
        # as we will check only basic json serialization property
        path = t.paths.all()[0]

        # Reload as the geom of the topology will be build by trigger
        t.reload()

        test_objdict = dict(kind=t.kind,
                       offset=1,
                       # 0 referencing the index in paths of the only created path
                       positions={},
                       paths=[ path.pk ]
                       )

        objdict = simplejson.loads(t.serialize())
        self.assertDictEqual(objdict, test_objdict)

    def test_serialize_point(self):
        path = PathFactory.create()
        topology = TopologyFactory.create(offset=1, no_path=True)
        topology.add_path(path, start=0.5, end=0.5)
        fieldvalue = topology.serialize()
        # fieldvalue is like '{"lat": -5.983842291017086, "lng": -1.3630770374505987, "kind": "TOPOLOGYMIXIN"}'
        field = simplejson.loads(fieldvalue)
        self.assertTrue(almostequal(field['lat'],  -5.983))
        self.assertTrue(almostequal(field['lng'],  -1.363))
        self.assertEqual(field['kind'],  "TOPOLOGY")

    def test_deserialize(self):
        path = PathFactory.create()
        topology = Topology.deserialize('{"paths": [%s], "positions": {"0": [0.0, 1.0]}, "offset": 1}' % (path.pk))
        self.assertEqual(topology.offset, 1)
        self.assertEqual(topology.kind, Topology.KIND)
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(topology.aggregations.all()[0].path, path)
        self.assertEqual(topology.aggregations.all()[0].start_position, 0.0)
        self.assertEqual(topology.aggregations.all()[0].end_position, 1.0)
        
        # Multiple paths
        p1 = PathFactory.create(geom=LineString((0,0,0), (2,2,2)))
        p2 = PathFactory.create(geom=LineString((2,2,2), (2,0,0)))
        p3 = PathFactory.create(geom=LineString((2,0,0), (4,0,0)))
        pks = [p.pk for p in [p1,p2,p3]]
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

        # With intermediate markers
        # Bad ones (start!=end)
        self.assertRaises(ValueError, Topology.deserialize, '{"paths": %s, "positions": {"0": [0.3, 1.0], "1": [0.2, 0.3], "2": [0.0, 0.7]}}' % pks)
        # Good ones
        topology = Topology.deserialize('{"paths": %s, "positions": {"0": [0.3, 1.0], "1": [0.5, 0.5], "2": [0.0, 0.7]}}' % pks)
        self.assertEqual(len(topology.paths.all()), 3)

    def test_deserialize_point(self):
        PathFactory.create()
        # Take a point
        p = Point(2, 1, 0, srid=settings.SRID)
        p.transform(settings.API_SRID)
        closest = Path.closest(p)
        # Check closest path
        self.assertEqual(closest.geom.coords, ((1.0, 1.0, 0.0), (2.0, 2.0, 0.0)))
        # The point has same x as first point of path, and y to 0 :
        topology = Topology.deserialize('{"lng": %s, "lat": %s}' % (p.x, p.y))
        self.assertAlmostEqual(topology.offset, -0.7071, 3)
        self.assertEqual(len(topology.paths.all()), 1)
        pagg = topology.aggregations.get()
        self.assertTrue(almostequal(pagg.start_position, 0.5))
        self.assertTrue(almostequal(pagg.end_position, 0.5))

    def test_deserialize_serialize(self):
        path = PathFactory.create(geom=LineString((1,1,1), (2,2,2), (2,0,0)))
        before = TopologyFactory.create(offset=1, no_path=True)
        before.add_path(path, start=0.5, end=0.5)
        # Reload from DB
        before = Topology.objects.get(pk=before.pk)
        
        # Deserialize its serialized version !
        after = Topology.deserialize(before.serialize())
        # Reload from DB
        after = Topology.objects.get(pk=after.pk)
        

        self.assertEqual(len(before.paths.all()), len(after.paths.all()))
        self.assertTrue(almostequal(before.aggregations.all()[0].start_position,
                                    after.aggregations.all()[0].start_position))
        self.assertTrue(almostequal(before.aggregations.all()[0].end_position,
                                    after.aggregations.all()[0].end_position))

    def test_junction_point(self):
        p1 = PathFactory.create(geom=LineString((0,0,0), (2,2,2)))
        p2 = PathFactory.create(geom=LineString((0,0,0), (2,0,0)))
        p3 = PathFactory.create(geom=LineString((0,2,2), (0,0,0)))

        # Create a junction point topology
        t = TopologyFactory.create(no_path=True)
        self.assertEqual(len(t.paths.all()), 0)

        pa = PathAggregationFactory.create(topo_object=t, path=p1,
                                      start_position=0.0, end_position=0.0)

        self.assertItemsEqual(t.paths.all(), [p1, p2, p3])

        # Update to a non junction point topology
        pa.end_position=0.4
        pa.save()

        self.assertItemsEqual(t.paths.all(), [p1])

        # Update to a junction point topology
        pa.end_position=0.0
        pa.save()

        self.assertItemsEqual(t.paths.all(), [p1, p2, p3])

    def test_topology_geom(self):
        p1 = PathFactory.create(geom=LineString((0,0,0), (2,2,2)))
        p2 = PathFactory.create(geom=LineString((2,2,2), (2,0,0)))
        p3 = PathFactory.create(geom=LineString((2,0,0), (4,0,0)))

        # Type Point
        t = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t, path=p1,
                                      start_position=0.5, end_position=0.5)
        t = Topology.objects.get(pk=t.pk)
        self.assertEqual(t.geom, Point((1,1,1)))

        # 50% of path p1, 100% of path p2
        t = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t, path=p1,
                                      start_position=0.5)
        PathAggregationFactory.create(topo_object=t, path=p2)
        t = Topology.objects.get(pk=t.pk)
        self.assertEqual(t.geom, LineString((1,1,1), (2,2,2), (2,0,0)))

        # 100% of path p2 and p3, with offset of 1
        t = TopologyFactory.create(no_path=True, offset=1)
        PathAggregationFactory.create(topo_object=t, path=p2)
        PathAggregationFactory.create(topo_object=t, path=p3)
        t.save()
        self.assertEqual(t.geom, LineString((3,2,2), (3,1,0), (4,1,0)))

        # Change offset, geometry is computed again
        t.offset = 0.5
        t.save()
        self.assertEqual(t.geom, LineString((2.5,2,2), (2.5,0.5,0), (4,0.5,0)))

    def test_topology_geom_with_intermediate_markers(self):
        # Intermediate (forced passage) markers for topologies
        # Use a bifurcation, make sure computed geometry is correct
        #       +--p2---+
        #   +---+-------+---+
        #     p1   p3     p4
        p1 = PathFactory.create(geom=LineString((0,0,0), (2,0,0)))
        p2 = PathFactory.create(geom=LineString((2,0,0), (2,1,0), (4,1,0), (4,0,0)))
        p3 = PathFactory.create(geom=LineString((2,0,0), (4,0,0)))
        p4 = PathFactory.create(geom=LineString((4,0,0), (6,0,0)))
        """
        From p1 to p4, with point in the middle of p3
        """
        t = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t, path=p1)
        PathAggregationFactory.create(topo_object=t, path=p3, 
                                      start_position=0.5, end_position=0.5)
        PathAggregationFactory.create(topo_object=t, path=p4)
        t.save()
        self.assertEqual(t.geom, LineString((0,0,0), (2,0,0), (4,0,0), (6,0,0)))
        """
        From p1 to p4, through p2
        """
        t = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t, path=p1)
        PathAggregationFactory.create(topo_object=t, path=p2, 
                                      start_position=0.5, end_position=0.5)
        PathAggregationFactory.create(topo_object=t, path=p4)
        t.save()
        self.assertEqual(t.geom, LineString((0,0,0), (2,0,0), (2,1,0), (4,1,0), (4,0,0), (6,0,0)))

        """
        From p1 to p4, though p2, but **with start/end at 0.0**
        """
        t2 = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t2, path=p1)
        PathAggregationFactory.create(topo_object=t2, path=p2, 
                                      start_position=0.0, end_position=0.0)
        PathAggregationFactory.create(topo_object=t2, path=p4)
        t2.save()
        print t2.pk, t2.geom.coords
        self.assertEqual(t2.geom, t.geom)

    def test_troncon_geom_update(self):
        p = PathFactory.create(geom=LineString((0,0,0), (2,2,0)))
        t = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t, path=p, start_position=0.5)
        t.reload()
        self.assertEqual(t.geom, LineString((1,1,0), (2,2,0)))
        p.geom = LineString((0,0,0), (0,2,0), (2,2,0))
        p.save()
        t.reload()
        self.assertEqual(t.geom, LineString((0,2,0), (2,2,0)))


class TrailTest(TestCase):

    def test_geom(self):
        t = TrailFactory.create()
        self.assertTrue(t.geom is None)
        p = PathFactory.create()
        t.paths.add(p)
        self.assertFalse(t.geom is None)
