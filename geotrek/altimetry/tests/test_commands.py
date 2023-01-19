import os
from io import StringIO
from unittest import mock, skipIf

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management import call_command, CommandError
from django.test import TransactionTestCase

from geotrek.altimetry.functions import RasterValue
from geotrek.altimetry.models import Dem

from geotrek.core.models import Path
from geotrek.core.tests.factories import PathFactory
from geotrek.trekking.models import Trek
from geotrek.trekking.tests.factories import TrekFactory

from django.contrib.gis.geos import LineString


class CommandLoadDemTest(TransactionTestCase):
    """
    Load dem command test
    Use of TransactionTestCase to avoid nesting transaction caused by raster2pgsql generated sql file import.
    """

    def test_success_without_replace(self):
        output_stdout = StringIO()
        filename = os.path.join(os.path.dirname(__file__), 'data', 'elevation.tif')
        call_command('loaddem', filename, verbosity=2, stdout=output_stdout)
        self.assertIn('DEM successfully loaded.', output_stdout.getvalue())
        self.assertIn('Everything looks fine, we can start loading DEM', output_stdout.getvalue())
        dems = Dem.objects.all().annotate(int=RasterValue('rast', Point(x=605600, y=6650000, srid=2154)))
        value = dems.first()
        self.assertAlmostEqual(value.int, 343.600006103516)

    def test_success_with_replace(self):
        output_stdout = StringIO()
        filename = os.path.join(os.path.dirname(__file__), 'data', 'elevation.tif')
        call_command('loaddem', filename, verbosity=2, stdout=output_stdout)
        self.assertIn('DEM successfully loaded.', output_stdout.getvalue())
        self.assertIn('Everything looks fine, we can start loading DEM', output_stdout.getvalue())
        raster_tiles = list(Dem.objects.all().values_list('pk', flat=True))
        call_command('loaddem', filename, '--replace', verbosity=2, stdout=output_stdout)
        self.assertFalse(Dem.objects.filter(pk__in=raster_tiles).exists())  # first imported tiles not exist anymore
        dems = Dem.objects.all().annotate(int=RasterValue('rast', Point(x=605600, y=6650000, srid=2154)))
        value = dems.first()
        self.assertAlmostEqual(value.int, 343.600006103516)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_success_without_replace_update_altimetry_ds(self):
        output_stdout = StringIO()
        filename = os.path.join(os.path.dirname(__file__), 'data', 'elevation.tif')
        self.path = PathFactory.create(geom=LineString((605600, 6650000), (605900, 6650010), srid=2154))
        trek = TrekFactory.create(paths=[self.path], published=False)
        call_command('loaddem', filename, update_altimetry=True, verbosity=2, stdout=output_stdout)
        self.assertIn('DEM successfully loaded.', output_stdout.getvalue())
        self.assertIn('Everything looks fine, we can start loading DEM', output_stdout.getvalue())
        self.assertIn('Updating 3d geometries.', output_stdout.getvalue())
        dems = Dem.objects.all().annotate(int=RasterValue('rast', Point(x=605600, y=6650000, srid=2154)))
        value = dems.first()
        self.assertAlmostEqual(value.int, 343.600006103516)
        path = Path.objects.get(pk=self.path.pk)
        self.assertAlmostEqual(path.geom_3d.coords[-1][-1], 188)
        trek = Trek.objects.get(pk=trek.pk)
        self.assertAlmostEqual(trek.geom_3d.coords[-1][-1], 188)

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
    def test_success_without_replace_update_altimetry_nds(self):
        output_stdout = StringIO()
        filename = os.path.join(os.path.dirname(__file__), 'data', 'elevation.tif')
        self.trek = TrekFactory.create(geom=LineString((605600, 6650000), (605900, 6650010), srid=2154))
        call_command('loaddem', filename, update_altimetry=True, verbosity=2, stdout=output_stdout)
        self.assertIn('DEM successfully loaded.', output_stdout.getvalue())
        self.assertIn('Everything looks fine, we can start loading DEM', output_stdout.getvalue())
        self.assertIn('Updating 3d geometries.', output_stdout.getvalue())
        dems = Dem.objects.all().annotate(int=RasterValue('rast', Point(x=605600, y=6650000, srid=2154)))
        value = dems.first()
        self.assertAlmostEqual(value.int, 343.600006103516)
        trek = Trek.objects.get(pk=self.trek.pk)
        self.assertAlmostEqual(trek.geom_3d.coords[-1][-1], 188)

    def test_fail_table_altimetry_dem(self):
        """ DEM data already exist """
        filename = os.path.join(os.path.dirname(__file__), 'data', 'elevation.tif')
        call_command('loaddem', filename, verbosity=0)
        with self.assertRaisesRegex(CommandError, 'DEM file exists, use --replace to overwrite'):
            call_command('loaddem', filename, verbosity=0)

    def test_fail_no_file(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'no.tif')
        with self.assertRaisesRegex(CommandError, 'DEM file does not exists at: %s' % filename):
            call_command('loaddem', filename, verbosity=0)

    def test_fail_wrong_format(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'test.xml')
        with self.assertRaisesRegex(CommandError, 'DEM format is not recognized by GDAL.'):
            call_command('loaddem', filename, verbosity=0)

    @mock.patch('geotrek.altimetry.management.commands.loaddem.Command.call_command_system')
    def test_fail_raster2pgsql_first(self, sp):
        def command_fail_raster(cmd, **kwargs):
            if 'raster2pgsql -G > /dev/null' in cmd:
                return 1
            return 0
        sp.side_effect = command_fail_raster
        filename = os.path.join(os.path.dirname(__file__), 'data', 'elevation.tif')
        with self.assertRaisesRegex(CommandError, 'Caught Exception: raster2pgsql failed with exit code 1'):
            call_command('loaddem', filename, '--replace', verbosity=0)

    @mock.patch('geotrek.altimetry.management.commands.loaddem.Command.call_command_system')
    def test_fail_raster2pgsql_second(self, sp):
        def command_fail_raster(cmd, **kwargs):
            if 'raster2pgsql -a -M -t' in cmd:
                return 1
            return 0
        sp.side_effect = command_fail_raster
        filename = os.path.join(os.path.dirname(__file__), 'data', 'elevation.tif')
        with self.assertRaisesRegex(CommandError, 'Caught Exception: raster2pgsql failed with exit code 1'):
            call_command('loaddem', filename, '--replace', verbosity=0)

    @mock.patch('geotrek.altimetry.management.commands.loaddem.GDALRaster')
    def test_fail_no_srid(self, mock_gdal_raster):
        """ No srs / srid defined in elevation file """
        mock_gdal_raster.return_value.srs = None
        filename = os.path.join(os.path.dirname(__file__), 'data', 'elevation.tif')
        with self.assertRaisesRegex(CommandError, 'DEM coordinate system is unknown.'):
            call_command('loaddem', filename, verbosity=0)

    def test_success_with_transformation(self):
        """ Test raster value with srs transformation """
        output_stdout = StringIO()
        filename = os.path.join(os.path.dirname(__file__), 'data', 'elevation_4326.tif')
        call_command('loaddem', filename, verbosity=2, stdout=output_stdout)
        self.assertIn('DEM successfully loaded.', output_stdout.getvalue())
        self.assertIn('Everything looks fine, we can start loading DEM', output_stdout.getvalue())
        dems = Dem.objects.all().annotate(int=RasterValue('rast', Point(x=605600, y=6650000, srid=2154)))
        value = dems.first()
        self.assertAlmostEqual(value.int, 343.600006103516)
