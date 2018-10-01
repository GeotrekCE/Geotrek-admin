from django.contrib.gis.geos import LineString
from django.core.management import call_command
from django.test import TestCase

from geotrek.core.models import Path
from geotrek.trekking.factories import POIFactory


class RemoveDuplicatePathTest(TestCase):

    def test_remove_no_duplicate_path(self):
        """
        This test check that we remove 1 of the duplicate path and keep ones with topologies.

                poi3 (only on p4)
        +-------o------+                    p5 is reversed.
        p3/p4/p5

        +-------o------+        +--------+
        p1/p2   poi1/poi2       p6

        We get at the end p1, p2, p4, p6.
        """
        p1 = Path.objects.create(name='First Path', geom=LineString((0, 0), (1, 0), (2, 0)))
        p2 = Path.objects.create(name='Second Path', geom=LineString((0, 0), (1, 0), (2, 0)))
        Path.objects.create(name='Third Path', geom=LineString((0, 2), (1, 2), (2, 2)))
        p4 = Path.objects.create(name='Fourth Path', geom=LineString((0, 2), (1, 2), (2, 2)))
        Path.objects.create(name='Fifth Path', geom=LineString((2, 2), (1, 2), (0, 2)))
        p6 = Path.objects.create(name='Sixth Path', geom=LineString((4, 0), (6, 0)))
        p7 = Path.objects.create(name='Seventh Path', geom=LineString((0, 6), (1, 6), (2, 6)))
        Path.objects.create(name='Eighth Path', geom=LineString((0, 6), (1, 6), (2, 6)))
        Path.objects.create(name='Nineth Path', geom=LineString((0, 6), (1, 6), (2, 6)))
        poi1 = POIFactory.create(name='POI1', no_path=True)
        poi1.add_path(p1, start=0.5, end=0.5)
        poi2 = POIFactory.create(name='POI2', no_path=True)
        poi2.add_path(p2, start=0.5, end=0.5)
        poi3 = POIFactory.create(name='POI3', no_path=True)
        poi3.add_path(p4, start=0.5, end=0.5)
        poi1.reload()
        poi2.reload()
        poi3.reload()
        self.assertEquals(Path.objects.count(), 9)
        call_command('remove_duplicate_paths', verbosity=0)
        self.assertEquals(Path.objects.count(), 5)
        self.assertItemsEqual((p1, p2, p4, p6, p7), Path.objects.all())
