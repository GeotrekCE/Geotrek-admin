from django.test import TestCase
from django.core import serializers

from caminae.core.models import Path


class GeoJsonSerializerTest (TestCase):
    def test_serializer(self):
        # Stuff to serialize
        Path(name='green').save()
        Path(name='blue').save()
        Path(name='red').save()

        # Expected output
        expect_geojson = \
            'myapp.color:\n' \
            '  1: {name: green}\n' \
            '  2: {name: blue}\n' \
            '  3: {name: red}\n'

        # Do the serialization
        actual_geojson = serializers.serialize('yaml', Path.objects.all())

        # Did it work?
        self.assertEqual(actual_geojson, expect_geojson)


class GeoJsonSerializerTest (TestCase):
    def test_deserializer(self):
        # Input text
        input_geojson = \
            'myapp.color:\n' \
            '  1: {name: green}\n' \
            '  2: {name: blue}\n' \
            '  3: {name: red}\n'

        # Deserialize into a list of objects
        objects = list(serializers.deserialize('geojson', input_geojson))

        # Were three objects deserialized?
        self.assertEqual(len(objects), 3)

        # Did the objects deserialize correctly?
        self.assertEqual(objects[0].object.name, 'green')
        self.assertEqual(objects[1].object.name, 'blue')
        self.assertEqual(objects[2].object.name, 'red')
