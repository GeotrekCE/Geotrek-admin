from tempfile import TemporaryDirectory
from io import StringIO
import os

from django.test import TestCase
from django.conf import settings
from django.contrib.gis import gdal
from django.contrib.gis.gdal import DataSource
from django.http import HttpResponse
from django.test.utils import override_settings
from django.utils import translation

from mapentity.serializers import ZipShapeSerializer, CSVSerializer
from mapentity.serializers.shapefile import shape_write, info_from_geo_field, geo_field_from_model
from mapentity.settings import app_settings

from geotrek.core.models import Path
from geotrek.core.factories import PathFactory
from geotrek.diving.factories import DiveFactory
from geotrek.diving.models import Dive, Difficulty
from geotrek.common.factories import ThemeFactory


class ShapefileSerializer(TestCase):
    def setUp(self):
        self.point1 = DiveFactory.create()
        self.point1.themes.add(ThemeFactory.create(label="Tag1"))
        self.point1.themes.add(ThemeFactory.create(label="Tag2"))
        self.line1 = DiveFactory.create(geom='SRID=%s;LINESTRING(0 0, 10 0)' % settings.SRID)
        self.multiline = DiveFactory.create(geom='SRID=%s;MULTILINESTRING((10 10, 20 20, 10 40),'
                                                 '(40 40, 30 30, 40 20, 30 10))' % settings.SRID)
        self.multipoint = DiveFactory.create(geom='SRID=%s;MULTIPOINT((1 1), (2 2))' % settings.SRID)
        self.polygon = DiveFactory.create(geom='SRID=%s;POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))' % settings.SRID)
        self.multipolygon = DiveFactory.create(geom='SRID=%s;MULTIPOLYGON(((0 0, 0 1, 1 1, 1 0, 0 0)),'
                                                    '((2 2, 2 3, 3 3, 3 2, 2 2)))' % settings.SRID)
        self.serializer = ZipShapeSerializer()
        response = HttpResponse()
        self.serializer.serialize(Dive.objects.all(), stream=response,
                                  fields=['id', 'name'], delete=False)

    def getShapefileLayers(self):
        shapefiles = self.serializer.path_directory
        shapefiles = [shapefile for shapefile in os.listdir(shapefiles) if shapefile[-3:] == "shp"]
        datasources = [gdal.DataSource(os.path.join(self.serializer.path_directory, s)) for s in shapefiles]
        layers = [ds[0] for ds in datasources]
        return layers

    def test_serializer_creates_one_layer_per_type(self):
        self.assertEqual(len(self.getShapefileLayers()), 6)

    def test_each_layer_has_records_by_type(self):
        layer_multipolygon, layer_linestring, layer_multilinestring, layer_point, \
            layer_multipoint, layer_polygon = self.getShapefileLayers()
        self.assertEqual(len(layer_point), 1)
        self.assertEqual(len(layer_linestring), 1)
        self.assertEqual(len(layer_multipoint), 1)
        self.assertEqual(len(layer_polygon), 1)
        self.assertEqual(len(layer_multilinestring), 1)
        self.assertEqual(len(layer_multipolygon), 1)

    def test_each_layer_has_a_different_geometry_type(self):
        layer_types = [layer.geom_type.name for layer in self.getShapefileLayers()]
        self.assertCountEqual(layer_types, ['LineString', 'Polygon', 'MultiPoint', 'Point', 'LineString', 'Polygon'])

    def test_layer_has_right_projection(self):
        for layer in self.getShapefileLayers():
            self.assertIn(layer.srs.name, ('RGF93_Lambert_93', 'RGF93 / Lambert-93'))
            self.assertCountEqual(layer.fields, ['id', 'name'])

    def test_geometries_come_from_records(self):
        layers = self.getShapefileLayers()
        geom_type_layer = {layer.name: layer for layer in layers}
        feature = geom_type_layer['Point'][0]
        self.assertEqual(str(feature['id']), str(self.point1.pk))
        self.assertTrue(feature.geom.geos.equals(self.point1.geom))

        feature = geom_type_layer['MultiPoint'][0]
        self.assertEqual(str(feature['id']), str(self.multipoint.pk))
        self.assertTrue(feature.geom.geos.equals(self.multipoint.geom))

        feature = geom_type_layer['LineString'][0]
        self.assertEqual(str(feature['id']), str(self.line1.pk))
        self.assertTrue(feature.geom.geos.equals(self.line1.geom))

        feature = geom_type_layer['MultiLineString'][0]
        self.assertEqual(str(feature['id']), str(self.multiline.pk))
        self.assertTrue(feature.geom.geos.equals(self.multiline.geom))

        feature = geom_type_layer['Polygon'][0]
        self.assertEqual(str(feature['id']), str(self.polygon.pk))
        self.assertTrue(feature.geom.geos.equals(self.polygon.geom))

        feature = geom_type_layer['MultiPolygon'][0]
        self.assertEqual(str(feature['id']), str(self.multipolygon.pk))
        self.assertTrue(feature.geom.geos.equals(self.multipolygon.geom))

    def test_attributes(self):
        layer_point, layer_linestring, layer_polygon, layer_multipoint, \
            layer_multilinestring, layer_multipolygon = self.getShapefileLayers()
        feature = layer_point[0]
        self.assertEqual(feature['name'].value, self.point1.name)

    def test_serializer_model_no_geofield(self):
        self.serializer = ZipShapeSerializer()
        response = HttpResponse()
        with self.assertRaisesRegex(ValueError, "No geodjango geometry fields found in this model"):
            self.serializer.serialize(Difficulty.objects.all(), stream=response,
                                      fields=['id', 'name'], delete=False)

    def test_serializer_model_geofield_multiple(self):
        app_settings['GEOM_FIELD_NAME'] = None
        self.serializer = ZipShapeSerializer()
        PathFactory.create()
        response = HttpResponse()
        with self.assertRaisesRegex(ValueError, "More than one geodjango geometry field found, please specify which "
                                                "to use by name using the 'geo_field' keyword. "
                                                "Available fields are: 'geom_3d, geom, geom_cadastre'"):
            self.serializer.serialize(Path.objects.all(), stream=response,
                                      fields=['id', 'name'], delete=False)
        app_settings['GEOM_FIELD_NAME'] = 'geom'

    def test_serializer_model_geofield_do_not_exist(self):
        app_settings['GEOM_FIELD_NAME'] = 'do_not_exist'
        self.serializer = ZipShapeSerializer()
        PathFactory.create()
        response = HttpResponse()
        with self.assertRaisesRegex(ValueError, "Geodjango geometry field not found with the name 'do_not_exist', "
                                                "fields available are: 'geom_3d, geom, geom_cadastre'"):
            self.serializer.serialize(Path.objects.all(), stream=response,
                                      fields=['id', 'name'], delete=False)
        app_settings['GEOM_FIELD_NAME'] = 'geom'

    def test_serializer_shape_write_special_srid(self):
        geo_field = geo_field_from_model(Dive, 'geom')
        get_geom, geom_type, srid = info_from_geo_field(geo_field)
        dives = [dive for dive in Dive.objects.all() if dive.geom.geom_type == 'Point']
        with TemporaryDirectory(dir=app_settings['TEMP_DIR']) as tmp_directory:
            shape_write(tmp_directory,
                        dives, Dive, ['id', 'name'], get_geom, 'Point', 2154, 3812)
            ds = DataSource(os.path.join(tmp_directory, 'Point.shp'))

        layer = ds[0]
        for feature in layer:
            self.assertAlmostEqual(feature.geom.x, -315454.73811014)
            self.assertAlmostEqual(feature.geom.y, -6594196.36395467)


class CSVSerializerTests(TestCase):
    def setUp(self):
        self.point = DiveFactory.create(name="Test")
        self.point.themes.add(ThemeFactory.create(label="Tag1"))
        self.point.themes.add(ThemeFactory.create(label="Tag2"))
        self.serializer = CSVSerializer()
        self.stream = StringIO()

    def tearDown(self):
        self.stream.close()

    def test_content(self):
        self.serializer.serialize(Dive.objects.all(), stream=self.stream,
                                  fields=['id', 'name'], delete=False)
        self.assertEqual(self.stream.getvalue(),
                         ('ID,Name\r\n{},'
                          'Test\r\n').format(self.point.pk))

    @override_settings(USE_L10N=True)
    def test_content_fr(self):
        translation.activate('fr')
        self.serializer.serialize(Dive.objects.all(), stream=self.stream,
                                  fields=['id', 'name'], delete=False)
        self.assertEqual(self.stream.getvalue(),
                         ('ID,Nom\r\n{},'
                          'Test\r\n').format(self.point.pk))
        translation.deactivate()
