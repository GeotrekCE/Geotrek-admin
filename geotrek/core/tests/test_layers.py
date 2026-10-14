from django.test import TestCase

from geotrek.core.layers import PathVectorLayer
from geotrek.core.tests.factories import PathFactory


class PathVectorLayerTest(TestCase):
    def test_get_queryset(self):
        path_named = PathFactory.create(name="Sentier des crêtes", visible=True)
        path_unnamed = PathFactory.create(name="", visible=True)
        path_invisible = PathFactory.create(name="Secret", visible=False)

        layer = PathVectorLayer()
        qs = layer.get_queryset()

        self.assertIn(path_named, qs)
        self.assertIn(path_unnamed, qs)
        self.assertNotIn(path_invisible, qs)

        for obj in qs:
            if obj.pk == path_named.pk:
                self.assertEqual(obj.name, "Sentier des crêtes")
            elif obj.pk == path_unnamed.pk:
                self.assertEqual(obj.name, f"path {path_unnamed.pk}")
