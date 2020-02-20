import os
from io import StringIO

from django.test import TestCase
from django.conf import settings
from django.contrib.gis.db.models import GeometryField
from django.contrib.gis import gdal
from django.http import HttpResponse
from django.test.utils import override_settings
from django.utils import translation

from mapentity.serializers import ZipShapeSerializer, CSVSerializer
from mapentity.serializers.shapefile import shapefile_files

from geotrek.diving.factories import DiveFactory
from geotrek.diving.models import Dive
from geotrek.common.factories import ThemeFactory


class ShapefileSerializer(TestCase):
    def setUp(self):
        self.point1 = DiveFactory.create()
        self.point1.themes.add(ThemeFactory.create(label="Tag1"))
        self.point1.themes.add(ThemeFactory.create(label="Tag2"))
        self.line1 = DiveFactory.create(geom='SRID=%s;LINESTRING(0 0, 10 0)' % settings.SRID)
        self.multipoint = DiveFactory.create(geom='SRID=%s;MULTIPOINT((1 1), (2 2))' % settings.SRID)

        self.serializer = ZipShapeSerializer()
        response = HttpResponse()
        self.serializer.serialize(Dive.objects.all(), stream=response,
                                  fields=['id', 'name'], delete=False)

    def tearDown(self):
        for layer_file in self.serializer.layers.values():
            for subfile in shapefile_files(layer_file):
                os.remove(subfile)

    def getShapefileLayers(self):
        shapefiles = self.serializer.layers.values()
        datasources = [gdal.DataSource(s) for s in shapefiles]
        layers = [ds[0] for ds in datasources]
        return layers

    def test_serializer_creates_one_layer_per_type(self):
        self.assertEquals(len(self.serializer.layers), 3)

    def test_each_layer_has_records_by_type(self):
        layer_point, layer_multipoint, layer_linestring = self.getShapefileLayers()
        self.assertEquals(len(layer_point), 1)
        self.assertEquals(len(layer_linestring), 1)
        self.assertEquals(len(layer_multipoint), 1)

    def test_each_layer_has_a_different_geometry_type(self):
        layer_types = [l.geom_type.name for l in self.getShapefileLayers()]
        self.assertCountEqual(layer_types, ['MultiPoint', 'Point', 'LineString'])

    def test_layer_has_right_projection(self):
        for layer in self.getShapefileLayers():
            self.assertIn(layer.srs.name, ('RGF93_Lambert_93', 'RGF93 / Lambert-93'))
            self.assertCountEqual(layer.fields, ['id', 'name'])

    def test_geometries_come_from_records(self):
        layer_point, layer_multipoint, layer_linestring = self.getShapefileLayers()
        feature = layer_point[0]
        self.assertEquals(str(feature['id']), str(self.point1.pk))
        self.assertTrue(feature.geom.geos.equals(self.point1.geom))

        feature = layer_point[0]
        self.assertEquals(str(feature['id']), str(self.point1.pk))
        self.assertTrue(feature.geom.geos.equals(self.point1.geom))

        feature = layer_point[0]
        self.assertEquals(str(feature['id']), str(self.point1.pk))
        self.assertTrue(feature.geom.geos.equals(self.point1.geom))

    def test_attributes(self):
        layer_point, layer_multipoint, layer_linestring = self.getShapefileLayers()
        feature = layer_point[0]
        self.assertEquals(feature['name'].value, self.point1.name)


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
        self.assertEquals(self.stream.getvalue(),
                          ('ID,Name\r\n{},'
                           'Test\r\n').format(self.point.pk))

    @override_settings(USE_L10N=True)
    def test_content_fr(self):
        translation.activate('fr-fr')
        self.serializer.serialize(Dive.objects.all(), stream=self.stream,
                                  fields=['id', 'name'], delete=False)
        self.assertEquals(self.stream.getvalue(),
                          ('ID,Nom\r\n{},'
                           'Test\r\n').format(self.point.pk))
        translation.deactivate()
