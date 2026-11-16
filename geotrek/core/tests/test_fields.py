import json
from unittest import mock

from django.contrib.gis.forms import GeometryField
from django.contrib.gis.geos import LineString, Point
from django.core.exceptions import ValidationError
from django.test import TestCase

from geotrek.core.fields import (
    PointLineTopoGeomField,
    PointTopoGeomField,
    TopologyField,
)
from geotrek.core.models import Topology
from geotrek.core.tests.factories import PathFactory


class TopologyFieldTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.f = TopologyField()

    def test_validation_fails_if_null_is_submitted(self):
        self.assertRaises(ValidationError, self.f.clean, "null")

    def test_empty_not_required(self):
        f = TopologyField(required=False)
        self.assertIsNone(f.clean(""))

    def test_empty_required(self):
        f = TopologyField(required=True)
        with self.assertRaises(ValidationError):
            f.clean("")

    def test_unknown_topology_pk(self):
        with self.assertRaises(ValidationError):
            self.f.clean("999999")

    def test_invalid_topology_string(self):
        with self.assertRaises(ValidationError):
            self.f.clean("invalid-string-not-topology")


class PointTopoGeomFieldTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path = PathFactory.create()
        cls.field = PointTopoGeomField()

    def test_empty_not_required(self):
        field = PointTopoGeomField(required=False)
        self.assertIsNone(field.clean(""))

    def test_empty_required(self):
        field = PointTopoGeomField(required=True)
        with self.assertRaises(ValidationError):
            field.clean("")

    def test_missing_coordinates(self):
        with self.assertRaises(ValidationError):
            self.field.clean(json.dumps({"snapFeature": self.path.pk}))

    def test_valid_point_with_snap(self):
        data = json.dumps({"coordinates": [1.4, 43.6], "snapFeature": self.path.pk})
        topo = self.field.clean(data)
        self.assertIsInstance(topo, Topology)

    def test_valid_point_without_snap(self):
        data = json.dumps({"coordinates": [1.4, 43.6]})
        topo = self.field.clean(data)
        self.assertIsInstance(topo, Topology)

    def test_topology_does_not_exist(self):
        data = json.dumps({"coordinates": [1.4, 43.6]})
        with mock.patch(
            "geotrek.core.fields.Topology.deserialize",
            side_effect=Topology.DoesNotExist,
        ):
            with self.assertRaises(ValidationError):
                self.field.clean(data)

    def test_value_error(self):
        data = json.dumps({"coordinates": [1.4, 43.6], "snapFeature": 999999})
        with self.assertRaises(ValidationError):
            self.field.clean(data)


class PointLineTopoGeomFieldTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path = PathFactory.create()
        cls.field = PointLineTopoGeomField()

    def test_init_target_map(self):
        field = PointLineTopoGeomField(target_map="test-map")
        self.assertEqual(field.widget.attrs.get("target_map"), "test-map")

    def test_empty_not_required(self):
        field = PointLineTopoGeomField(required=False)
        self.assertIsNone(field.clean(""))

    def test_empty_required(self):
        field = PointLineTopoGeomField(required=True)
        with self.assertRaises(ValidationError):
            field.clean("")

    def test_clean_linestring(self):
        data = json.dumps(
            {"type": "LineString", "coordinates": [[1.4, 43.6], [1.5, 43.7]]}
        )
        geom = self.field.clean(data)
        self.assertIsInstance(geom, LineString)

    def test_clean_polygon_rejected(self):
        data = json.dumps(
            {
                "type": "Polygon",
                "coordinates": [[[1, 1], [2, 1], [2, 2], [1, 2], [1, 1]]],
            }
        )
        with self.assertRaises(ValidationError) as cm:
            self.field.clean(data)
        self.assertIn(
            "The geometry should either be a point or a line.", str(cm.exception)
        )

    def test_clean_point_missing_coordinates(self):
        with mock.patch.object(GeometryField, "clean", return_value=Point(1, 1)):
            with self.assertRaises(ValidationError) as cm:
                self.field.clean(json.dumps({"type": "Point"}))
            self.assertIn(
                "Point geometry is incorrect (missing coordinates).", str(cm.exception)
            )

    def test_clean_point_with_snap(self):
        data = json.dumps(
            {"type": "Point", "coordinates": [1.4, 43.6], "snapFeature": self.path.pk}
        )
        topo = self.field.clean(data)
        self.assertIsInstance(topo, Topology)

    def test_clean_point_without_snap(self):
        data = json.dumps({"type": "Point", "coordinates": [1.4, 43.6]})
        topo = self.field.clean(data)
        self.assertIsInstance(topo, Topology)

    def test_clean_point_topology_does_not_exist(self):
        data = json.dumps({"type": "Point", "coordinates": [1.4, 43.6]})
        with mock.patch(
            "geotrek.core.fields.Topology.deserialize",
            side_effect=Topology.DoesNotExist,
        ):
            with self.assertRaises(ValidationError):
                self.field.clean(data)

    def test_clean_point_value_error(self):
        data = json.dumps(
            {"type": "Point", "coordinates": [1.4, 43.6], "snapFeature": 999999}
        )
        with self.assertRaises(ValidationError) as cm:
            self.field.clean(data)
        self.assertIn("User input error", str(cm.exception))
