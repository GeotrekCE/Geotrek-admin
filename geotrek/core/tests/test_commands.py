from StringIO import StringIO

from django.contrib.gis.geos import LineString
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.db import IntegrityError

from geotrek.authent.models import Structure
from geotrek.core.models import Path
from geotrek.trekking.factories import POIFactory
import os


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
        self.assertItemsEqual((self.p1, self.p3, self.p5, self.p6, self.p8),
                              list(Path.objects.all()))
        self.assertIn("Deleting path",
                      output.getvalue())
        self.assertIn("duplicate paths have been deleted",
                      output.getvalue())


class LoadPathsCommandTest(TestCase):
    def setUp(self):
        self.filename = os.path.join(os.path.dirname(__file__), 'data', 'paths.geojson')
        self.structure = Structure.objects.create(name='huh')

    def test_load_paths_without_file(self):
        with self.assertRaises(CommandError) as e:
            call_command('loadpaths')
        self.assertEqual(u'Error: too few arguments', e.exception.message)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(5, 10.0, 5, 11))
    def test_load_paths_out_of_spatial_extent(self):
        call_command('loadpaths', self.filename, srid=4326, no_dry=True, verbosity=0)
        self.assertEquals(Path.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -1, 1, 5))
    def test_load_paths_within_spatial_extent(self):
        call_command('loadpaths', self.filename, srid=4326, no_dry=True, verbosity=0)
        self.assertEquals(Path.objects.count(), 1)
        value = Path.objects.first()
        self.assertEqual(value.name, 'lulu')
        self.assertEqual(value.structure, self.structure)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -1, 1, 5))
    def test_load_paths_intersect_spatial_extent(self):
        output = StringIO()
        call_command('loadpaths', self.filename, '-i', srid=4326, no_dry=True, verbosity=2, stdout=output)
        output = output.getvalue()
        self.assertIn('All paths in DataSource will be linked to the structure : %s' % self.structure.name, output)
        self.assertEquals(Path.objects.count(), 1)
        path = Path.objects.first()
        self.assertIn('Create path with pk : %s' % path.pk, output)
        value = Path.objects.first()
        self.assertEqual(value.name, 'lulu')
        self.assertEqual(value.structure, self.structure)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, 0, 4, 2))
    def test_load_paths_intersect_spatial_extent_2(self):
        output = StringIO()
        call_command('loadpaths', self.filename, '-i', srid=4326, no_dry=True, verbosity=2,
                     stdout=output)
        output = output.getvalue()
        self.assertIn('All paths in DataSource will be linked to the structure : %s' % self.structure.name, output)
        self.assertEquals(Path.objects.count(), 2)
        paths = Path.objects.all()
        self.assertIn('Create path with pk : %s' % paths[0].pk, output)
        self.assertIn('Create path with pk : %s' % paths[1].pk, output)
        value = Path.objects.first()
        self.assertEqual(value.name, 'lulu')
        self.assertEqual(value.structure, self.structure)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, 0, 4, 2))
    def test_load_paths_not_within_spatial_extent(self):
        output = StringIO()
        filename = os.path.join(os.path.dirname(__file__), 'data', 'point.geojson')
        call_command('loadpaths', filename, structure=self.structure.name, srid=4326, no_dry=True, verbosity=2, stdout=output)
        self.assertIn("Feature FID 0 in Layer<OGRGeoJSON>'s geometry is not a Linestring", output.getvalue())

    def test_load_paths_fail_bad_srid(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'bad_srid.geojson')
        with self.assertRaises(CommandError) as e:
            call_command('loadpaths', filename, no_dry=True, verbosity=0)
        self.assertEqual('SRID is not well configurate, change/add option srid', e.exception.message)

    def test_load_paths_with_bad_structure(self):
        with self.assertRaises(CommandError) as e:
            call_command('loadpaths', self.filename, structure='gr', no_dry=True, verbosity=0)
        self.assertIn("Structure does not match with instance's structures", e.exception.message)

    def test_load_paths_with_multiple_structure(self):
        Structure.objects.create(name='other_structure')
        with self.assertRaises(CommandError) as e:
            call_command('loadpaths', self.filename, no_dry=True, verbosity=0)
        self.assertIn("There are more than 1 structure and you didn't define the option structure\n"
                      "Use --structure to define it", e.exception.message)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, 0, 4, 2))
    def test_load_paths_dry(self):
        output = StringIO()
        call_command('loadpaths', self.filename, '-i', no_dry=False, verbosity=2, stdout=output)
        self.assertIn('2 objects will be create, 0 objects failed;', output.getvalue())
        self.assertEqual(Path.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, 0, 4, 2))
    def test_load_paths_fail_with_dry(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'bad_path.geojson')
        output = StringIO()
        call_command('loadpaths', filename, '-i', no_dry=False, verbosity=2, stdout=output)
        self.assertIn('0 objects will be create, 1 objects failed;', output.getvalue())
        self.assertEqual(Path.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, 0, 4, 2))
    def test_load_paths_fail_without_dry(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'bad_path.geojson')
        output = StringIO()
        with self.assertRaises(IntegrityError):
            call_command('loadpaths', filename, '-i', no_dry=True, verbosity=2, stdout=output)
