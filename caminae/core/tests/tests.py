from django.test import TestCase
from django.conf import settings
from django.utils import simplejson
from django.contrib.gis.geos import Point, LineString, Polygon, MultiPolygon
from django.db import connections, DEFAULT_DB_ALIAS

from caminae.mapentity.tests import MapEntityTest
from caminae.common.utils import dbnow, almostequal
from caminae.authent.factories import UserFactory, PathManagerFactory
from caminae.authent.models import Structure, default_structure
from caminae.core.factories import PathFactory, PathAggregationFactory, TopologyMixinFactory
from caminae.core.models import Path, TopologyMixin, TopologyMixinKind

# TODO caminae.core should be self sufficient
from caminae.land.models import (City, RestrictedArea, LandEdge)
from caminae.land.factories import LandEdgeFactory


class ViewsTest(MapEntityTest):
    model = Path
    modelfactory = PathFactory
    userfactory = PathManagerFactory

    def get_bad_data(self):
        baddata, msg = super(ViewsTest, self).get_bad_data()
        return baddata, u'Acune valeur g\xe9om\xe9trique fournie.'

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


class PathTest(TestCase):
    def test_paths_bystructure(self):
        user = UserFactory()
        p1 = PathFactory()
        p2 = PathFactory(structure=Structure.objects.create(name="other"))

        self.assertEqual(user.profile.structure, p1.structure)
        self.assertNotEqual(user.profile.structure, p2.structure)

        self.assertEqual(len(Structure.objects.all()), 2)
        self.assertEqual(len(Path.objects.all()), 2)

        self.assertEqual(Path.in_structure.byUser(user)[0], Path.forUser(user)[0])
        self.assertTrue(p1 in Path.in_structure.byUser(user))
        self.assertFalse(p2 in Path.in_structure.byUser(user))

        # Change user structure on-the-fly
        profile = user.profile
        profile.structure = p2.structure
        profile.save()

        self.assertEqual(user.profile.structure.name, "other")
        self.assertFalse(p1 in Path.in_structure.byUser(user))
        self.assertTrue(p2 in Path.in_structure.byUser(user))

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
        p = PathAggregationFactory.create(topo_object=e)
        e.save()
        self.assertNotEqual(e.length, 0)

    def test_kind(self):
        self.assertEqual('TopologyMixin', TopologyMixin.get_kind().kind)
        self.assertEqual(0, len(TopologyMixinKind.objects.filter(kind='LandEdge')))
        self.assertEqual('LandEdge', LandEdge.get_kind().kind)
        self.assertEqual(1, len(TopologyMixinKind.objects.filter(kind='LandEdge')))
        pk = LandEdge.get_kind().pk
        # Kind of instances
        e = LandEdgeFactory.create()
        self.assertEqual(e.kind, LandEdge.get_kind())
        self.assertEqual(pk, e.get_kind().pk)

    def test_serialize(self):
        topology = TopologyMixinFactory.create(offset=1)
        self.assertEqual(len(topology.paths.all()), 1)
        path = topology.paths.all()[0]
        kind = topology.kind.kind
        fieldvalue = topology.serialize()
        self.assertEqual(fieldvalue, '{"paths": [%s], "kind": "%s", "end": 1.0, "start": 0.0, "offset": 1}' % (path.pk, kind))
    
    def test_serialize_point(self):
        path = PathFactory.create()
        topology = TopologyMixinFactory.create(offset=1, no_path=True)
        topology.add_path(path, start=0.5, end=0.5)
        fieldvalue = topology.serialize()
        # fieldvalue is like '{"lat": -5.983842291017086, "lng": -1.3630770374505987, "kind": "TopologyMixin"}'
        field = simplejson.loads(fieldvalue)
        self.assertTrue(almostequal(field['lat'],  -5.983))
        self.assertTrue(almostequal(field['lng'],  -1.363))
        self.assertEqual(field['kind'],  "TopologyMixin")

    def test_deserialize(self):
        path = PathFactory.create()
        topology = TopologyMixin.deserialize('{"paths": [%s], "start": 0.0, "end": 1.0, "offset": 1}' % (path.pk))
        self.assertEqual(topology.offset, 1)
        self.assertEqual(topology.kind, TopologyMixin.get_kind())
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(topology.aggregations.all()[0].path, path)
        self.assertEqual(topology.aggregations.all()[0].start_position, 0.0)
        self.assertEqual(topology.aggregations.all()[0].end_position, 1.0)

    def test_deserialize_point(self):
        PathFactory.create()
        # Take a point
        p = Point(0, 2.0, 0, srid=settings.SRID)
        p.transform(settings.API_SRID)
        closest = Path.closest(p)
        # Check closest path
        self.assertEqual(closest.geom.coords, ((1.0, 1.0, 0.0), (2.0, 2.0, 0.0)))
        # The point has same x as first point of path, and y to 0 :
        topology = TopologyMixin.deserialize('{"lng": %s, "lat": %s}' % (p.x, p.y))
        self.assertTrue(almostequal(topology.offset, 1.414))
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertTrue(almostequal(topology.aggregations.all()[0].start_position, 7.34463799778595e-07))
        self.assertTrue(almostequal(topology.aggregations.all()[0].end_position, 7.34463799778595e-07))

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
