from django.test import TestCase
from django.core import serializers

from caminae.core.models import Path


class GeoJsonSerializerTest (TestCase):
    def test_serializer(self):
        # Stuff to serialize
        Path(name='green', geom="LINESTRING (0 0, 1 1)").save()
        Path(name='blue', geom="LINESTRING (0 0, 1 1)").save()
        Path(name='red', geom="LINESTRING (0 0, 1 1)").save()

        # Expected output
        expect_geojson = """{"type": "FeatureCollection", "features": [{"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"pk": 1, "model": "core.path", "valid": true, "name": "green"}, "id": 1}, {"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"pk": 2, "model": "core.path", "valid": true, "name": "blue"}, "id": 2}, {"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"pk": 3, "model": "core.path", "valid": true, "name": "red"}, "id": 3}]}"""

        # Do the serialization
        actual_geojson = serializers.serialize('geojson', Path.objects.all(), fields=['name', 'valid'])

        # Did it work?
        self.assertEqual(actual_geojson, expect_geojson)


    def test_deserializer(self):
        # Input text
        input_geojson = """
        
        {"type": "FeatureCollection",
         "features": [
            { "type": "Feature",
                "properties": {"model": "core.Path", "name": "green"},
                "id": 1,
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [0.0, 0.0],
                        [1.0, 1.0]
                    ]
                }
            }
        ]}"""
        
        # Deserialize into a list of objects
        objects = list(serializers.deserialize('geojson', input_geojson))

        # Were three objects deserialized?
        self.assertEqual(len(objects), 1)

        # Did the objects deserialize correctly?
        self.assertEqual(objects[0].object.name, "green")
