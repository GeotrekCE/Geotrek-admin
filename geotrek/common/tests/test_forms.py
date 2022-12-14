import json
from django.test import TestCase
from geotrek.common.forms import HDViewPointAnnotationForm
from geotrek.common.tests.factories import HDViewPointFactory, LicenseFactory


class HDViewPointAnnotateFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vp = HDViewPointFactory(content_object=LicenseFactory())

    def test_annotation_form(self):
        geojson = '{"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [7903.518111498841, 3618.542606516288]}, "properties": {"name": "Test point", "annotationId": 13, "annotationType": "point"}}]}'
        data = {
            "annotations": geojson
        }
        form = HDViewPointAnnotationForm(instance=self.vp, data=data)
        form.save()
        self.assertEqual(self.vp.annotations, json.loads(geojson))
