import os
from io import StringIO
from unittest.mock import patch
from unittest import skipIf

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry

from geotrek.core.factories import PathFactory
from geotrek.trekking.models import POI
from geotrek.trekking.management.commands.loadpoi import Command


class LoadPOITest(TestCase):
    def setUp(self):
        self.cmd = Command()
        self.filename = os.path.join(os.path.dirname(__file__),
                                     'data', 'poi.shp')
        self.path = PathFactory.create()

    def test_command_shows_number_of_objects(self):
        output = StringIO()
        call_command('loadpoi', self.filename, verbosity=1, stdout=output)
        self.assertIn('2 objects found', output.getvalue())

    def test_create_pois_is_executed(self):
        with patch.object(Command, 'create_poi') as mocked:
            self.cmd.handle(point_layer=self.filename, verbosity=0, encoding='utf-8')
            self.assertEqual(mocked.call_count, 2)

    def test_create_pois_receives_geometries(self):
        with patch.object(Command, 'create_poi') as mocked:
            self.cmd.handle(point_layer=self.filename, verbosity=0, encoding='utf-8')
            call1 = mocked.call_args_list[0][0]
            call2 = mocked.call_args_list[1][0]
            self.assertAlmostEqual(call1[0].x, -1.3630867, places=7)
            self.assertAlmostEqual(call1[0].y, -5.9835847, places=7)
            self.assertAlmostEqual(call2[0].x, -1.3630872, places=7)
            self.assertAlmostEqual(call2[0].y, -5.9835842, places=7)
            self.assertEqual(call1[0].geom_type, 'Point')

    def test_create_pois_receives_fields_names_and_types(self):
        with patch.object(Command, 'create_poi') as mocked:
            self.cmd.handle(point_layer=self.filename, verbosity=0, encoding='utf-8')
            call1 = mocked.call_args_list[0][0]
            call2 = mocked.call_args_list[1][0]
            self.assertEqual(call1[1], 'pont')
            self.assertEqual(call2[1], 'pancarte 1')
            self.assertEqual(call1[2], 'équipement')
            self.assertEqual(call2[2], 'signaletique')

    def test_create_pois_receives_null_if_field_missing(self):
        self.cmd.field_name = 'name2'
        with patch.object(Command, 'create_poi') as mocked:
            self.cmd.handle(point_layer=self.filename, verbosity=0, encoding='utf-8')
            call1 = mocked.call_args_list[0][0]
            self.assertEqual(call1[1], 'POI 1')

    def test_pois_are_created(self):
        geom = GEOSGeometry('POINT(1 1)', srid=4326)
        before = len(POI.objects.all())
        self.cmd.create_poi(geom, 'bridge', 'infra')
        after = len(POI.objects.all())
        self.assertEqual(after - before, 1)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_pois_are_attached_to_paths(self):
        geom = GEOSGeometry('POINT(1 1)', srid=4326)
        poi = self.cmd.create_poi(geom, 'bridge', 'infra')
        self.assertEqual([self.path], list(poi.paths.all()))
