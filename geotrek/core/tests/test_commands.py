from io import StringIO

from django.contrib.gis.geos import LineString
from django.core.management import call_command
from django.test import TestCase

from geotrek.core.models import Path
from geotrek.trekking.factories import POIFactory


class RemoveDuplicatePathTest(TestCase):
    def setUp(self):
        geom_1 = LineString((0, 0), (1, 0), (2, 0))
        self.p1 = Path.objects.create(name='First Path', geom=geom_1)
        self.p2 = Path.objects.create(name='Second Path', geom=geom_1)

        geom_2 = LineString((0, 2), (1, 2), (2, 2))
        self.p3 = Path.objects.create(name='Third Path', geom=geom_2)
        self.p4 = Path.objects.create(name='Fourth Path', geom=geom_2)

        geom_3 = LineString((2, 2), (1, 2), (0, 2))
        self.p5 = Path.objects.create(name='Fifth Path', geom=geom_3)

        geom_4 = LineString((4, 0), (6, 0))

        self.p6 = Path.objects.create(name='Sixth Path', geom=geom_4)
        self.p7 = Path.objects.create(name='Seventh Path', geom=geom_4)

        geom_5 = LineString((0, 6), (1, 6), (2, 6))

        self.p8 = Path.objects.create(name='Eighth Path', geom=geom_5)
        self.p9 = Path.objects.create(name='Nineth Path', geom=geom_5)

        poi1 = POIFactory.create(name='POI1', no_path=True)
        poi1.add_path(self.p1, start=0.5, end=0.5)
        poi2 = POIFactory.create(name='POI2', no_path=True)
        poi2.add_path(self.p2, start=0.5, end=0.5)
        poi3 = POIFactory.create(name='POI3', no_path=True)
        poi3.add_path(self.p4, start=0.5, end=0.5)

    def test_remove_duplicate_path(self):
        """
        This test check that we remove 1 of the duplicate path and keep ones with topologies.

                poi3 (only on p4)
        +-------o------+                    p5 is reversed.
        p3/p4/p5

        +-------o------+        +--------+
        p1/p2   poi1/poi2       p6

        We get at the end p1, p3, p5, p6.
        """
        output = StringIO()
        call_command('remove_duplicate_paths', verbosity=2, stdout=output)

        self.assertEquals(Path.objects.count(), 5)
        self.assertCountEqual((self.p1, self.p3, self.p5, self.p6, self.p8),
                              list(Path.objects.all()))
        self.assertIn("Deleting path",
                      output.getvalue())
        self.assertIn("duplicate paths have been deleted",
                      output.getvalue())
