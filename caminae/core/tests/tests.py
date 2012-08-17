from django.test import TestCase
from django.conf import settings
from django.contrib.gis.geos import LineString, Polygon, MultiPolygon
from django.db import connections, DEFAULT_DB_ALIAS

from caminae.mapentity.tests import MapEntityTest
from caminae.common.utils import dbnow
from caminae.authent.factories import UserFactory, PathManagerFactory
from caminae.authent.models import Structure, default_structure
from caminae.core.factories import PathFactory, TopologyMixinFactory
from caminae.core.models import Path, TopologyMixin, TopologyMixinKind

# TODO caminae.core should be self sufficient
from caminae.land.models import (City, RestrictedArea, LandEdge)
from caminae.land.factories import LandEdgeFactory


class ViewsTest(MapEntityTest):
    model = Path
    modelfactory = PathFactory
    userfactory = PathManagerFactory

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
        e = TopologyMixinFactory.build()
        e.save()
        t2 = dbnow()
        self.assertTrue(t1 < e.date_insert < t2)

        e.deleted = True
        e.save()
        t3 = dbnow()
        self.assertTrue(t2 < e.date_update < t3)

    def test_length(self):
        e = TopologyMixinFactory.build()
        self.assertEqual(e.length, 0)
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
