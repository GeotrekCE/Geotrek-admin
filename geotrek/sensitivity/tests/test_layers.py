import math

import mercantile
from django.conf import settings
from django.contrib.gis.geos import Point
from django.test import TestCase

from geotrek.sensitivity.tests.factories import SensitiveAreaFactory, SpeciesFactory
from geotrek.sensitivity.vector_layers import SensitivityVectorLayer


class SensitivityVectorLayerTest(TestCase):
    def test_point_uses_species_radius_circle(self):
        species = SpeciesFactory.create(radius=300)
        area = SensitiveAreaFactory.create(
            geom=Point(700000, 6600000, srid=settings.SRID), species=species
        )

        layer = SensitivityVectorLayer()
        obj = layer.get_queryset().get(pk=area.pk)

        self.assertEqual(obj.geom_display.geom_type, "Polygon")
        self.assertAlmostEqual(
            obj.geom_display.area, math.pi * 300**2, delta=math.pi * 300**2 * 0.02
        )

    def test_point_without_radius_uses_default_radius(self):
        species = SpeciesFactory.create(radius=None)
        area = SensitiveAreaFactory.create(
            geom=Point(700000, 6600000, srid=settings.SRID), species=species
        )

        layer = SensitivityVectorLayer()
        obj = layer.get_queryset().get(pk=area.pk)

        expected_radius = settings.SENSITIVITY_DEFAULT_RADIUS
        self.assertEqual(obj.geom_display.geom_type, "Polygon")
        self.assertAlmostEqual(
            obj.geom_display.area,
            math.pi * expected_radius**2,
            delta=math.pi * expected_radius**2 * 0.02,
        )

    def test_point_with_zero_radius_stays_point(self):
        species = SpeciesFactory.create(radius=0)
        area = SensitiveAreaFactory.create(
            geom=Point(700000, 6600000, srid=settings.SRID), species=species
        )

        layer = SensitivityVectorLayer()
        obj = layer.get_queryset().get(pk=area.pk)

        self.assertEqual(obj.geom_display.geom_type, "Point")

    def test_polygon_keeps_original_geometry_and_excludes_deleted(self):
        area_poly = SensitiveAreaFactory.create()
        area_deleted = SensitiveAreaFactory.create()
        area_deleted.delete()

        layer = SensitivityVectorLayer()
        qs = layer.get_queryset()

        self.assertIn(area_poly, qs)
        self.assertNotIn(area_deleted, qs)
        obj = qs.get(pk=area_poly.pk)
        self.assertEqual(obj.geom_display.geom_type, "Polygon")
        self.assertAlmostEqual(obj.geom_display.area, area_poly.geom.area)

    def test_get_tile_generates_mvt_bytes(self):
        species = SpeciesFactory.create(radius=300)
        area = SensitiveAreaFactory.create(
            geom=Point(700000, 6600000, srid=settings.SRID), species=species
        )
        point_wgs84 = area.geom.transform(4326, clone=True)
        tile_coords = mercantile.tile(point_wgs84.x, point_wgs84.y, 12)

        layer = SensitivityVectorLayer()
        tile = layer.get_tile(tile_coords.x, tile_coords.y, tile_coords.z)

        self.assertIsInstance(tile, bytes)
        self.assertGreater(len(tile), 0)
