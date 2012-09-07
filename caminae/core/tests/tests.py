from django.test import TestCase
from django.conf import settings
from django.utils import simplejson
from django.contrib.gis.geos import Point, LineString, Polygon, MultiPolygon
from django.db import connections, DEFAULT_DB_ALIAS, IntegrityError

# TODO caminae.core should be self sufficient
from caminae.land.models import (City, RestrictedArea, LandEdge)
from caminae.mapentity.tests import MapEntityTest
from caminae.common.utils import dbnow, almostequal
from caminae.authent.factories import UserFactory, PathManagerFactory, StructureFactory
from caminae.authent.models import Structure, default_structure
from caminae.core.factories import (PathFactory, PathAggregationFactory, 
    TopologyMixinFactory, StakeFactory)
from caminae.maintenance.factories import InterventionFactory, ProjectFactory
from caminae.infrastructure.factories import InfrastructureFactory, SignageFactory
from caminae.land.factories import LandEdgeFactory
from caminae.core.models import Path, TopologyMixin, PathAggregation


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
            'trail': '',
            'comments': '',
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

    def test_couches_sig_link(self):
        # Fake restricted areas
        ra1 = RestrictedArea(name='Zone 1', order=1, geom=MultiPolygon(
            Polygon(((0,0), (2,0), (2,1), (0,1), (0,0)))))
        ra1.save()
        ra2 = RestrictedArea(name='Zone 2', order=1, geom=MultiPolygon(
            Polygon(((0,1), (2,1), (2,2), (0,2), (0,1)))))
        ra2.save()

        # Fake city
        c = City(code='005178', name='Trifouillis-les-marmottes',
                 geom=MultiPolygon(Polygon(((0,0), (2,0), (2,2), (0,2), (0,0)),
                              srid=settings.SRID)))
        c.save()

        # Fake paths in these areas
        p = PathFactory(geom=LineString((0.5,0.5,0), (1.5,1.5,0)))
        p.save()

        # This should results in 3 PathAggregation (2 for RA, 1 for City)
        self.assertEquals(p.aggregations.count(), 3)

        # PathAgg is plain for City
        pa = c.cityedge_set.get().aggregations.get()
        self.assertEquals(pa.start_position, 0.0)
        self.assertEquals(pa.end_position, 1.0)

        # PathAgg is splitted in 2 parts for RA
        self.assertEquals(ra1.restrictedareaedge_set.count(), 1)
        self.assertEquals(ra2.restrictedareaedge_set.count(), 1)
        pa1 = ra1.restrictedareaedge_set.get().aggregations.get()
        pa2 = ra2.restrictedareaedge_set.get().aggregations.get()
        self.assertEquals(pa1.start_position, 0.0)
        self.assertEquals(pa1.end_position, 0.5)
        self.assertEquals(pa2.start_position, 0.5)
        self.assertEquals(pa2.end_position, 1.0)

        # Ensure everything is in order after update
        p.geom = LineString((0.5,0.5,0), (1.5,0.5,0))
        p.save()
        self.assertEquals(ra1.restrictedareaedge_set.count(), 1)
        self.assertEquals(ra2.restrictedareaedge_set.count(), 0)
        pa1 = ra1.restrictedareaedge_set.get().aggregations.get()
        self.assertEquals(pa1.start_position, 0.0)
        self.assertEquals(pa1.end_position, 1.0)

        # All intermediary objects should be cleaned on delete
        p.delete()
        self.assertEquals(c.cityedge_set.count(), 0)
        self.assertEquals(ra1.restrictedareaedge_set.count(), 0)
        self.assertEquals(ra2.restrictedareaedge_set.count(), 0)

    def test_helpers(self):
        p = PathFactory.create()

        self.assertEquals(len(p.interventions), 0)
        self.assertEquals(len(p.projects), 0)
        self.assertEquals(len(p.lands), 0)
        self.assertEquals(len(p.signages), 0)
        self.assertEquals(len(p.infrastructures), 0)

        sign = SignageFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=sign, path=p,
                                      start_position=0.5, end_position=0.5)

        self.assertItemsEqual(p.signages, [sign])

        infra = InfrastructureFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=infra, path=p)

        self.assertItemsEqual(p.infrastructures, [infra])

        i1 = InterventionFactory.create()
        i1.set_infrastructure(sign)
        i1.save()

        self.assertItemsEqual(p.interventions, [i1])

        i2 = InterventionFactory.create()
        i2.set_infrastructure(infra)
        i2.save()

        self.assertItemsEqual(p.interventions, [i1, i2])

        proj = ProjectFactory.create()
        proj.interventions.add(i1)
        proj.interventions.add(i2)

        self.assertItemsEqual(p.projects, [proj])

        l = LandEdgeFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=l, path=p)

        self.assertItemsEqual(p.lands, [l])

    def test_geom_update(self):
        # Create a path
        p = PathFactory.create(geom=LineString((0,0,0),(4,0,0)))

        # Create a linear topology
        t1 = TopologyMixinFactory.create(offset=1, no_path=True)
        t1.add_path(p, start=0.0, end=0.5)
        t1_agg = t1.aggregations.get()

        # Create a point topology
        t2 = TopologyMixinFactory.create(offset=-1, no_path=True)
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


class TopologyMixinTest(TestCase):
    def test_dates(self):
        t1 = dbnow()
        e = TopologyMixinFactory.build(no_path=True)
        e.save()
        t2 = dbnow()
        self.assertTrue(t1 < e.date_insert < t2)

        e.deleted = True
        e.save()
        t3 = dbnow()
        self.assertTrue(t2 < e.date_update < t3)

    def test_length(self):
        e = TopologyMixinFactory.build(no_path=True)
        self.assertEqual(e.length, 0)
        e.save()
        self.assertEqual(e.length, 0)
        PathAggregationFactory.create(topo_object=e)
        e.save()
        self.assertNotEqual(e.length, 0)

    def test_kind(self):
        self.assertEqual('TOPOLOGYMIXIN', TopologyMixin.KIND)
        self.assertEqual(0, len(TopologyMixin.objects.filter(kind='LANDEDGE')))
        self.assertEqual('LANDEDGE', LandEdge.KIND)
        # Kind of instances
        e = LandEdgeFactory.create()
        self.assertEqual(e.kind, LandEdge.KIND)
        self.assertEqual(1, len(TopologyMixin.objects.filter(kind='LANDEDGE')))

    def test_delete(self):
        # Make sure it deletes in cascade
        topology = TopologyMixinFactory.create(offset=1)
        self.assertEqual(len(PathAggregation.objects.filter(topo_object=topology)), 1)
        topology.delete()
        self.assertEqual(len(PathAggregation.objects.filter(topo_object=topology)), 0)

    def test_mutate(self):
        topology1 = TopologyMixinFactory.create(no_path=True)
        self.assertEqual(len(topology1.paths.all()), 0)
        topology2 = TopologyMixinFactory.create(offset=14.5)
        self.assertEqual(len(topology2.paths.all()), 1)
        # Normal usecase
        topology1.mutate(topology2)
        self.assertEqual(topology1.offset, 14.5)
        self.assertEqual(len(topology1.paths.all()), 1)
        # topology2 does not exist anymore
        self.assertEqual(len(TopologyMixin.objects.filter(pk=topology2.pk)), 0)
        # Without deletion
        topology3 = TopologyMixinFactory.create()
        topology1.mutate(topology3, delete=False)
        # topology3 still exists
        self.assertEqual(len(TopologyMixin.objects.filter(pk=topology3.pk)), 1)

    def test_serialize(self):
        # At least two path are required
        t = TopologyMixinFactory.create(offset=1)
        self.assertEqual(len(t.paths.all()), 1)

        # This path as been created automatically
        # as we will check only basic json serialization property
        path = t.paths.all()[0]

        # Reload as the geom of the topology will be build by trigger
        t.reload()

        # Create our objectdict to serialize

        geom = Point(t.geom.coords[0], srid=settings.SRID)
        start_point = geom.transform(settings.API_SRID, clone=True)

        geom = Point(t.geom.coords[-1], srid=settings.SRID)
        end_point = geom.transform(settings.API_SRID, clone=True)

        test_objdict = dict(kind=t.kind,
                       offset=1,
                       # 0 referencing the index in paths of the only created path
                       positions={'0': [0.0, 1.0]},
                       paths=[ path.pk ],
                       start_point=dict(lng=start_point.x, lat=start_point.y),
                       end_point=dict(lng=end_point.x, lat=end_point.y),
                       )

        objdict = simplejson.loads(t.serialize())
        self.assertDictEqual(objdict, test_objdict)

    def test_serialize_point(self):
        path = PathFactory.create()
        topology = TopologyMixinFactory.create(offset=1, no_path=True)
        topology.add_path(path, start=0.5, end=0.5)
        fieldvalue = topology.serialize()
        # fieldvalue is like '{"lat": -5.983842291017086, "lng": -1.3630770374505987, "kind": "TOPOLOGYMIXIN"}'
        field = simplejson.loads(fieldvalue)
        self.assertTrue(almostequal(field['lat'],  -5.983))
        self.assertTrue(almostequal(field['lng'],  -1.363))
        self.assertEqual(field['kind'],  "TOPOLOGYMIXIN")

    def test_deserialize(self):
        path = PathFactory.create()
        topology = TopologyMixin.deserialize('{"paths": [%s], "positions": {"0": [0.0, 1.0]}, "offset": 1}' % (path.pk))
        self.assertEqual(topology.offset, 1)
        self.assertEqual(topology.kind, TopologyMixin.KIND)
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(topology.aggregations.all()[0].path, path)
        self.assertEqual(topology.aggregations.all()[0].start_position, 0.0)
        self.assertEqual(topology.aggregations.all()[0].end_position, 1.0)
        
        # Multiple paths
        p1 = PathFactory.create(geom=LineString((0,0,0), (2,2,2)))
        p2 = PathFactory.create(geom=LineString((2,2,2), (2,0,0)))
        p3 = PathFactory.create(geom=LineString((2,0,0), (4,0,0)))
        pks = [p.pk for p in [p1,p2,p3]]
        topology = TopologyMixin.deserialize('{"paths": %s, "positions": {"0": [0.0, 1.0], "2": [0.0, 1.0]}, "offset": 1}' % (pks))
        for i in range(3):
            self.assertEqual(topology.aggregations.all()[i].start_position, 0.0)
            self.assertEqual(topology.aggregations.all()[i].end_position, 1.0)

        topology = TopologyMixin.deserialize('{"paths": %s, "positions": {"0": [0.3, 1.0], "2": [0.0, 0.7]}, "offset": 1}' % (pks))
        self.assertEqual(topology.aggregations.all()[0].start_position, 0.3)
        self.assertEqual(topology.aggregations.all()[0].end_position, 1.0)
        self.assertEqual(topology.aggregations.all()[1].start_position, 0.0)
        self.assertEqual(topology.aggregations.all()[1].end_position, 1.0)
        self.assertEqual(topology.aggregations.all()[2].start_position, 0.0)
        self.assertEqual(topology.aggregations.all()[2].end_position, 0.7)

    def test_deserialize_point(self):
        PathFactory.create()
        # Take a point
        p = Point(2, 1, 0, srid=settings.SRID)
        p.transform(settings.API_SRID)
        closest = Path.closest(p)
        # Check closest path
        self.assertEqual(closest.geom.coords, ((1.0, 1.0, 0.0), (2.0, 2.0, 0.0)))
        # The point has same x as first point of path, and y to 0 :
        topology = TopologyMixin.deserialize('{"lng": %s, "lat": %s}' % (p.x, p.y))
        self.assertAlmostEqual(topology.offset, -0.7071, 3)
        self.assertEqual(len(topology.paths.all()), 1)
        pagg = topology.aggregations.get()
        self.assertTrue(almostequal(pagg.start_position, 0.5))
        self.assertTrue(almostequal(pagg.end_position, 0.5))

    def test_deserialize_serialize(self):
        path = PathFactory.create(geom=LineString((1,1,1), (2,2,2), (2,0,0)))
        before = TopologyMixinFactory.create(offset=1, no_path=True)
        before.add_path(path, start=0.5, end=0.5)
        # Reload from DB
        before = TopologyMixin.objects.get(pk=before.pk)
        
        # Deserialize its serialized version !
        after = TopologyMixin.deserialize(before.serialize())
        # Reload from DB
        after = TopologyMixin.objects.get(pk=after.pk)
        

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
        t = TopologyMixinFactory.create(no_path=True)
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

        t = TopologyMixinFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t, path=p1,
                                      start_position=0.5, end_position=0.5)
        t = TopologyMixin.objects.get(pk=t.pk)
        self.assertEqual(t.geom, Point((1,1,1)))

        t = TopologyMixinFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t, path=p1,
                                      start_position=0.5)
        PathAggregationFactory.create(topo_object=t, path=p2)
        t = TopologyMixin.objects.get(pk=t.pk)
        self.assertEqual(t.geom, LineString((1,1,1), (2,2,2), (2,0,0)))

        t = TopologyMixinFactory.create(no_path=True, offset=1)
        PathAggregationFactory.create(topo_object=t, path=p2)
        PathAggregationFactory.create(topo_object=t, path=p3)
        t.save()
        self.assertEqual(t.geom, LineString((3,2,2), (3,1,0), (4,1,0)))

        t.offset = 0.5
        t.save()
        self.assertEqual(t.geom, LineString((2.5,2,2), (2.5,0.5,0), (4,0.5,0)))

    def test_troncon_geom_update(self):
        p = PathFactory.create(geom=LineString((0,0,0), (2,2,0)))
        t = TopologyMixinFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=t, path=p, start_position=0.5)
        t.reload()
        self.assertEqual(t.geom, LineString((1,1,0), (2,2,0)))
        p.geom = LineString((0,0,0), (0,2,0), (2,2,0))
        p.save()
        t.reload()
        self.assertEqual(t.geom, LineString((0,2,0), (2,2,0)))
