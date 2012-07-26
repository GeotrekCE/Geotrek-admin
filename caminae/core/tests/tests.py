from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.gis.geos import LineString, Polygon, MultiPolygon
from django.core.urlresolvers import reverse

from caminae.utils import dbnow
from caminae.authent.models import Structure
from caminae.core.models import (TopologyMixin, TopologyMixinKind,
                                 Path)
from caminae.land.models import (City, RestrictedArea)


class ViewsTest(TestCase):
    def test_status(self):
        response = self.client.get(reverse("core:layer_path"))
        self.assertEqual(response.status_code, 200)


class PathTest(TestCase):
    def setUp(self):
        self.structure = Structure(name="other")
        self.structure.save()

    def test_paths_bystructure(self):
        user = User.objects.create_user('Joe', 'temporary@yopmail.com', 'Bar')
        self.assertEqual(user.profile.structure.name, settings.DEFAULT_STRUCTURE_NAME)

        p1 = Path(geom=LineString((0, 0), (1, 1), srid=settings.SRID))
        self.assertEqual(user.profile.structure.name, settings.DEFAULT_STRUCTURE_NAME)
        p1.save()

        p2 = Path(geom=LineString((0, 0), (1, 1), srid=settings.SRID))
        p2.structure = self.structure
        p2.save()

        self.assertEqual(len(Structure.objects.all()), 2)
        self.assertEqual(len(Path.objects.all()), 2)

        self.assertEqual(Path.in_structure.byUser(user)[0], Path.forUser(user)[0])
        self.assertTrue(p1 in Path.in_structure.byUser(user))
        self.assertFalse(p2 in Path.in_structure.byUser(user))

        p = user.profile
        p.structure = self.structure
        p.save()

        self.assertEqual(user.profile.structure.name, "other")

        self.assertFalse(p1 in Path.in_structure.byUser(user))
        self.assertTrue(p2 in Path.in_structure.byUser(user))

    def test_dates(self):
        t1 = dbnow()
        p = Path(geom=LineString((0, 0), (1, 1), srid=settings.SRID),
                 structure=self.structure)
        p.save()
        t2 = dbnow()
        self.assertTrue(t1 < p.date_insert < t2,
                        msg='Date interval failed: %s < %s < %s' % (
                            t1, p.date_insert, t2
                        ))

        p.geom = LineString((0, 0), (2, 2), srid=settings.SRID)
        p.save()
        t3 = dbnow()
        self.assertTrue(t2 < p.date_update < t3,
                        msg='Date interval failed: %s < %s < %s' % (
                            t2, p.date_update, t3
                       ))

    def test_length(self):
        p = Path(geom=LineString((0, 0), (1, 1), structure=self.structure))
        self.assertEqual(p.length, 0)
        p.save()
        self.assertNotEqual(p.length, 0)

    def test_couches_sig_link(self):
        s = Structure(name="other")
        s.save()

        # Fake restricted areas
        ra1 = RestrictedArea(code=1, name='Zone 1', order=1, geom=MultiPolygon(
            Polygon(((0,0), (2,0), (2,1), (0,1), (0,0)), srid=settings.SRID)))
        ra1.save()
        ra2 = RestrictedArea(code=2, name='Zone 2', order=1, geom=MultiPolygon(
            Polygon(((0,1), (2,1), (2,2), (0,2), (0,1)), srid=settings.SRID)))
        ra2.save()

        # Fake city
        c = City(code='005178', name='Trifouillis-les-marmottes',
                 geom=MultiPolygon(Polygon(((0,0), (2,0), (2,2), (0,2), (0,0)),
                              srid=settings.SRID)))
        c.save()

        # Fake paths in these areas
        p = Path(structure=s,
                 geom=LineString((0.5,0.5), (1.5,1.5), srid=settings.SRID))
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
        p.geom = LineString((0.5,0.5), (1.5,0.5), srid=settings.SRID)
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
    def setUp(self):
        self.k = TopologyMixinKind(kind="other")
        self.k.save()

    def test_dates(self):
        t1 = dbnow()
        e = TopologyMixin(geom=LineString((0, 0), (1, 1), srid=settings.SRID),
                          offset=0,
                          length=0,
                          deleted=False,
                          kind=self.k)
        e.save()
        t2 = dbnow()
        self.assertTrue(t1 < e.date_insert < t2)

        e.deleted = True
        e.save()
        t3 = dbnow()
        self.assertTrue(t2 < e.date_update < t3)

    def test_length(self):
        e = TopologyMixin(geom=LineString((0, 0), (1, 1)), kind=self.k)
        self.assertEqual(e.length, 0)
        e.save()
        self.assertNotEqual(e.length, 0)
