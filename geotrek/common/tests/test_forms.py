import json
from django.test import TestCase
from geotrek.common.forms import HDViewPointAnnotationForm
from geotrek.common.tests.factories import AnnotationCategoryFactory, HDViewPointFactory
from geotrek.trekking.tests.factories import TrekFactory


class HDViewPointAnnotateFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vp = HDViewPointFactory(content_object=TrekFactory())
        cls.annotationcategory = AnnotationCategoryFactory()

    def test_annotation_form(self):
        geojson = '{"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [7903.518111498841, 3618.542606516288]}, "properties": {"name": "Test point", "annotationId": 13, "annotationType": "point"}}]}'
        data = {
            "annotations": geojson,
            "annotations_categories": f'{{"13":"{self.annotationcategory.pk}"}}'
        }
        form = HDViewPointAnnotationForm(instance=self.vp, data=data)
        form.save()
        self.assertEqual(self.vp.annotations, json.loads(geojson))
        self.assertEqual(self.vp.annotations_categories, {'13': str(self.annotationcategory.pk)})

    def test_annotation_empty_values_form(self):
        data = {
            "annotations": "",
            "annotations_categories": ""
        }
        form = HDViewPointAnnotationForm(instance=self.vp, data=data)
        self.assertTrue(form.is_valid())
