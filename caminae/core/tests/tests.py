from django.test import TestCase
from django.conf import settings
from django.contrib.gis.geos import LineString, Polygon, MultiPolygon
from django.core.urlresolvers import reverse
from django.db import connections, DEFAULT_DB_ALIAS

from caminae.utils import dbnow
from caminae.authent.factories import UserFactory
from caminae.authent.models import Structure
from caminae.core.factories import PathFactory, TopologyMixinFactory, TopologyMixinKindFactory
from caminae.core.models import Path
from caminae.land.models import (City, RestrictedArea)


class ViewsTest(TestCase):
    def test_status(self):
        response = self.client.get(reverse("core:layer_path"))
        self.assertEqual(response.status_code, 200)


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
        self.assertEquals(p.pathaggregation_set.count(), 3)

        # PathAgg is plain for City
        pa = c.cityedge_set.get().pathaggregation_set.get()
        self.assertEquals(pa.start_position, 0.0)
        self.assertEquals(pa.end_position, 1.0)

        # PathAgg is splitted in 2 parts for RA
        self.assertEquals(ra1.restrictedareaedge_set.count(), 1)
        self.assertEquals(ra2.restrictedareaedge_set.count(), 1)
        pa1 = ra1.restrictedareaedge_set.get().pathaggregation_set.get()
        pa2 = ra2.restrictedareaedge_set.get().pathaggregation_set.get()
        self.assertEquals(pa1.start_position, 0.0)
        self.assertEquals(pa1.end_position, 0.5)
        self.assertEquals(pa2.start_position, 0.5)
        self.assertEquals(pa2.end_position, 1.0)

        # Ensure everything is in order after update
        p.geom = LineString((0.5,0.5,0), (1.5,0.5,0))
        p.save()
        self.assertEquals(ra1.restrictedareaedge_set.count(), 1)
        self.assertEquals(ra2.restrictedareaedge_set.count(), 0)
        pa1 = ra1.restrictedareaedge_set.get().pathaggregation_set.get()
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
        e = TopologyMixinFactory()
        e.save()
        t2 = dbnow()
        self.assertTrue(t1 < e.date_insert < t2)

        e.deleted = True
        e.save()
        t3 = dbnow()
        self.assertTrue(t2 < e.date_update < t3)

    def test_length(self):
        e = TopologyMixinFactory.build(kind=TopologyMixinKindFactory())
        self.assertEqual(e.length, 0)
        e.save()
        self.assertNotEqual(e.length, 0)
