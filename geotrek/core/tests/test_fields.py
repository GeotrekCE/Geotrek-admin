from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import LineString
from django.core.exceptions import ValidationError
from django.test import TestCase

from geotrek.core.fields import SnappedLineStringField, TopologyField
from geotrek.core.tests.factories import PathFactory


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class SnappedLineStringFieldTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.f = SnappedLineStringField()
        cls.wktgeom = (
            "LINESTRING(-0.77054223313507 -5.32573853776343,"
            "-0.168053647782867 -4.66595028627023)"
        )
        cls.geojson = (
            '{"type":"LineString","coordinates":['
            " [-0.77054223313507,-5.32573853776343],"
            " [-0.168053647782867,-4.66595028627023]]}"
        )

    def test_dict_with_geom_is_mandatory(self):
        self.assertRaises(ValidationError, self.f.clean, "LINESTRING(0 0, 1 0)")
        self.assertRaises(
            ValidationError, self.f.clean, '{"geo": "LINESTRING(0 0, 1 0)"}'
        )

    def test_snaplist_is_mandatory(self):
        self.assertRaises(
            ValidationError, self.f.clean, '{"geom": "LINESTRING(0 0, 1 0)"}'
        )

    def test_snaplist_must_have_same_number_of_vertices(self):
        self.assertRaises(
            ValidationError,
            self.f.clean,
            '{"geom": "LINESTRING(0 0, 1 0)", "snap": [null]}',
        )

    def test_geom_cannot_be_invalid_wkt(self):
        self.assertRaises(
            ValidationError,
            self.f.clean,
            '{"geom": "LINEPPRING(0 0, 1 0)", "snap": [null, null]}',
        )

    def test_geom_can_be_geojson(self):
        geojsonstr = self.geojson.replace('"', '\\"')
        geom = self.f.clean('{"geom": "%s",  "snap": [null, null]}' % geojsonstr)
        self.assertTrue(
            geom.equals_exact(
                LineString((100000, 100000), (200000, 200000), srid=settings.SRID), 0.1
            )
        )

    def test_geom_is_not_snapped_if_snap_is_null(self):
        value = '{"geom": "%s", "snap": [null, null]}' % self.wktgeom
        self.assertTrue(
            self.f.clean(value).equals_exact(
                LineString((100000, 100000), (200000, 200000), srid=settings.SRID), 0.1
            )
        )

    def test_geom_is_snapped_if_path_pk_is_provided(self):
        path = PathFactory.create()
        value = '{"geom": "%s", "snap": [null, %s]}' % (self.wktgeom, path.pk)
        self.assertTrue(
            self.f.clean(value).equals_exact(
                LineString((100000, 100000), (700000, 6600000), srid=settings.SRID), 0.1
            )
        )


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class TopologyFieldTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.f = TopologyField()

    def test_validation_fails_if_null_is_submitted(self):
        self.assertRaises(ValidationError, self.f.clean, "null")
