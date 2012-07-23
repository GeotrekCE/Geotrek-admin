from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.gis.geos import LineString
from django.core.urlresolvers import reverse

from caminae.authent.models import Structure
from caminae.core.models import Path


class ViewsTest(TestCase):
    def test_status(self):
        response = self.client.get(reverse("core:layerpath"))
        self.assertEqual(response.status_code, 200)

class PathTest(TestCase):
    def test_paths_bystructure(self):
        user = User.objects.create_user('Joe', 'temporary@yopmail.com', 'Bar')
        self.assertEqual(user.profile.structure.name, settings.DEFAULT_STRUCTURE_NAME)
        
        p1 = Path(geom=LineString((0, 0), (1, 1), srid=settings.SRID))
        self.assertEqual(user.profile.structure.name, settings.DEFAULT_STRUCTURE_NAME)
        p1.save()

        structure = Structure(name="other")
        structure.save()

        p2 = Path(geom=LineString((0, 0), (1, 1), srid=settings.SRID))
        p2.structure = structure
        p2.save()

        self.assertEqual(len(Structure.objects.all()), 2)
        self.assertEqual(len(Path.objects.all()), 2)
        
        self.assertEqual(Path.in_structure.byUser(user)[0], Path.forUser(user)[0])
        self.assertTrue(p1 in Path.in_structure.byUser(user))
        self.assertFalse(p2 in Path.in_structure.byUser(user))
        
        p = user.profile
        p.structure = structure
        p.save()
        
        self.assertEqual(user.profile.structure.name, "other")
        
        self.assertFalse(p1 in Path.in_structure.byUser(user))
        self.assertTrue(p2 in Path.in_structure.byUser(user))
