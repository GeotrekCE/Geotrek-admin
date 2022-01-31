from io import StringIO
from unittest import mock, skipIf

from django.conf import settings
from django.contrib.gis.geos import LineString
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.db import IntegrityError

from geotrek.authent.models import Structure
from geotrek.core.models import Path
from geotrek.trekking.tests.factories import POIFactory
import os


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class RemoveDuplicatePathTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        geom_1 = LineString((0, 0), (1, 0), (2, 0))
        cls.p1 = Path.objects.create(name='First Path', geom=geom_1)
        cls.p2 = Path.objects.create(name='Second Path', geom=geom_1)

        geom_2 = LineString((0, 2), (1, 2), (2, 2))
        cls.p3 = Path.objects.create(name='Third Path', geom=geom_2)
        cls.p4 = Path.objects.create(name='Fourth Path', geom=geom_2)

        geom_3 = LineString((2, 2), (1, 2), (0, 2))
        cls.p5 = Path.objects.create(name='Fifth Path', geom=geom_3)

        geom_4 = LineString((4, 0), (6, 0))

        cls.p6 = Path.objects.create(name='Sixth Path', geom=geom_4)
        cls.p7 = Path.objects.create(name='Seventh Path', geom=geom_4)

        geom_5 = LineString((0, 6), (1, 6), (2, 6))

        cls.p8 = Path.objects.create(name='Eighth Path', geom=geom_5)
        cls.p9 = Path.objects.create(name='Nineth Path', geom=geom_5)

        POIFactory.create(name='POI1', paths=[(cls.p1, 0.5, 0.5)])
        POIFactory.create(name='POI2', paths=[(cls.p2, 0.5, 0.5)])
        POIFactory.create(name='POI3', paths=[(cls.p4, 0.5, 0.5)])

    def test_remove_duplicate_path(self):
        """
        This test check that we remove 1 of the duplicate path and keep ones with topologies.

                poi3 (only on p4)
        +-------o------+                    p5 is reversed.
        p3/p4/p5
                poi1/poi2
        +-------o------+        +--------+
        p1/p2                     p6

        We get at the end p1, p3, p5, p6.
        """
        output = StringIO()
        call_command('remove_duplicate_paths', verbosity=2, stdout=output)

        self.assertEqual(Path.objects.count(), 5)
        self.assertCountEqual((self.p1, self.p3, self.p5, self.p6, self.p8),
                              list(Path.objects.all()))
        self.assertIn("Deleting path",
                      output.getvalue())
        self.assertIn("duplicate paths have been deleted",
                      output.getvalue())

    def test_remove_duplicate_path_visible(self):
        """
        This test check that we remove 1 of the duplicate path and keep ones with topologies.

                poi3 (only on p4)
        +-------o------+                    p5 is reversed.
        p3/p4/p5

        +-------o------+        +--------+
        p1/p2   poi1/poi2       p6

        We get at the end p2, p3, p5, p6.
        """
        output = StringIO()
        self.p1.visible = False
        self.p1.save()
        # Will remove only p1 because not visible
        self.p3.visible = False
        self.p3.save()
        # will remove the second because both of them are not visible
        self.p4.visible = False
        self.p4.save()
        call_command('remove_duplicate_paths', verbosity=2, stdout=output)

        self.assertEqual(Path.include_invisible.count(), 5)
        self.assertEqual(Path.objects.count(), 4)
        self.assertCountEqual((self.p2, self.p3, self.p5, self.p6, self.p8),
                              list(Path.include_invisible.all()))
        self.assertCountEqual((self.p2, self.p5, self.p6, self.p8),
                              list(Path.objects.all()))
        self.assertIn("Deleting path",
                      output.getvalue())
        self.assertIn("duplicate paths have been deleted",
                      output.getvalue())

    def test_remove_duplicate_path_fail(self):
        output = StringIO()
        with mock.patch('geotrek.core.models.Path.delete') as mock_delete:
            mock_delete.side_effect = Exception('An ERROR')
            call_command('remove_duplicate_paths', verbosity=2, stdout=output)
        self.assertIn("An ERROR", output.getvalue())
        self.assertEqual(Path.include_invisible.count(), 9)
        self.assertEqual(Path.objects.count(), 9)
        self.assertIn("0 duplicate paths have been deleted",
                      output.getvalue())


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class LoadPathsCommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.filename = os.path.join(os.path.dirname(__file__), 'data', 'paths.geojson')
        cls.structure = Structure.objects.create(name='huh')

    def test_load_paths_without_file(self):
        with self.assertRaisesRegex(CommandError, 'Error: the following arguments are required: file_path'):
            call_command('loadpaths')

    @override_settings(SRID=4326, SPATIAL_EXTENT=(5, 10.0, 5, 11))
    def test_load_paths_out_of_spatial_extent(self):
        call_command('loadpaths', self.filename, srid=4326, verbosity=0)
        self.assertEqual(Path.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -1, 1, 5))
    def test_load_paths_within_spatial_extent(self):
        call_command('loadpaths', self.filename, srid=4326, verbosity=0)
        self.assertEqual(Path.objects.count(), 1)
        value = Path.objects.first()
        self.assertEqual(value.name, 'lulu')
        self.assertEqual(value.structure, self.structure)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -1, 1, 5))
    def test_load_paths_comments(self):
        output = StringIO()
        call_command('loadpaths', self.filename, srid=4326, verbosity=2, comment=['comment', 'foo'], stdout=output)
        output = output.getvalue()
        self.assertEqual(Path.objects.count(), 1)
        value = Path.objects.first()
        self.assertEqual(value.name, 'lulu')
        self.assertEqual(value.comments, 'Comment 2</br>foo2')
        self.assertEqual(value.structure, self.structure)
        self.assertIn('The comment %s was added on %s' % (value.comments, value.name), output)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -1, 1, 5))
    def test_load_paths_intersect_spatial_extent(self):
        output = StringIO()
        call_command('loadpaths', self.filename, '-i', srid=4326, verbosity=2, stdout=output)
        output = output.getvalue()
        self.assertIn('All paths in DataSource will be linked to the structure : %s' % self.structure.name, output)
        self.assertEqual(Path.objects.count(), 1)
        path = Path.objects.first()
        self.assertIn('Create path with pk : %s' % path.pk, output)
        value = Path.objects.first()
        self.assertEqual(value.name, 'lulu')
        self.assertEqual(value.structure, self.structure)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, 0, 4, 2))
    def test_load_paths_intersect_spatial_extent_2(self):
        output = StringIO()
        call_command('loadpaths', self.filename, '-i', srid=4326, verbosity=2,
                     stdout=output)
        output = output.getvalue()
        self.assertIn('All paths in DataSource will be linked to the structure : %s' % self.structure.name, output)
        self.assertEqual(Path.objects.count(), 2)
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
        call_command('loadpaths', filename, structure=self.structure.name, srid=4326, verbosity=2, stdout=output)
        self.assertRegex(output.getvalue(), "Feature FID 0 in Layer<(point|OGRGeoJSON)>'s geometry is not a Linestring")

    def test_load_paths_fail_bad_srid(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'bad_srid.geojson')
        with self.assertRaisesRegex(CommandError, 'SRID is not well configurate, change/add option srid'):
            call_command('loadpaths', filename, verbosity=0)

    def test_load_paths_with_bad_structure(self):
        with self.assertRaisesRegex(CommandError, "Structure does not match with instance's structures"):
            call_command('loadpaths', self.filename, structure='gr', verbosity=0)

    def test_load_paths_with_multiple_structure(self):
        Structure.objects.create(name='other_structure')
        with self.assertRaisesRegex(CommandError, "There are more than 1 structure and you didn't define the option structure\nUse --structure to define it"):
            call_command('loadpaths', self.filename, verbosity=0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, 0, 4, 2))
    def test_load_paths_dry(self):
        output = StringIO()
        call_command('loadpaths', self.filename, '-i', dry=True, verbosity=2, stdout=output)
        self.assertIn('2 objects will be create, 0 objects failed;', output.getvalue())
        self.assertEqual(Path.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, 0, 4, 2))
    def test_load_paths_fail_with_dry(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'bad_path.geojson')
        output = StringIO()
        call_command('loadpaths', filename, '-i', dry=True, verbosity=2, stdout=output)
        self.assertIn('0 objects will be create, 1 objects failed;', output.getvalue())
        self.assertEqual(Path.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, 0, 4, 2))
    def test_load_paths_fail_without_dry(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'bad_path.geojson')
        output = StringIO()
        with self.assertRaises(IntegrityError):
            call_command('loadpaths', filename, '-i', verbosity=2, stdout=output)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -1, 1, 5))
    def test_load_paths_within_spatial_extent_no_srid_geom(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'paths_no_srid.shp')
        call_command('loadpaths', filename, srid=4326, verbosity=0)
        self.assertEqual(Path.objects.count(), 1)
        value = Path.objects.first()
        self.assertEqual(value.name, 'lulu')
        self.assertEqual(value.structure, self.structure)
