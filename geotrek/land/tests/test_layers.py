from django.core.cache import cache
from django.test import TestCase, override_settings

from geotrek.land.layers import (
    CirculationEdgeVectorLayer,
    CompetenceEdgeVectorLayer,
    LandEdgeVectorLayer,
    PhysicalEdgeVectorLayer,
    SignageManagementEdgeVectorLayer,
    WorkManagementEdgeVectorLayer,
)
from geotrek.land.tests.factories import (
    CirculationEdgeFactory,
    CompetenceEdgeFactory,
    LandEdgeFactory,
    PhysicalEdgeFactory,
    SignageManagementEdgeFactory,
    WorkManagementEdgeFactory,
)


class EdgeVectorLayerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.physical_edge = PhysicalEdgeFactory.create()
        cls.land_edge = LandEdgeFactory.create()
        cls.circulation_edge = CirculationEdgeFactory.create()
        cls.competence_edge = CompetenceEdgeFactory.create()
        cls.signage_management_edge = SignageManagementEdgeFactory.create()
        cls.work_management_edge = WorkManagementEdgeFactory.create()

    def setUp(self):
        cache.clear()

    @override_settings(COLORS_POOL={"physicaledge": ["#ff0000", "#00ff00"]})
    def test_physical_edge_layer_with_colors_pool_and_cache(self):
        layer = PhysicalEdgeVectorLayer()

        # 1. First call populates cache
        qs1 = list(layer.get_queryset().values(*layer.tile_fields))
        self.assertEqual(len(qs1), 1)
        self.assertEqual(qs1[0]["color"], "#ff0000")

        # 2. Second call uses cache (hits `if not color_by_type` False branch)
        qs2 = list(layer.get_queryset().values(*layer.tile_fields))
        self.assertEqual(len(qs2), 1)
        self.assertEqual(qs2[0]["color"], "#ff0000")

    @override_settings(COLORS_POOL={})
    def test_physical_edge_layer_without_colors_pool(self):
        layer = PhysicalEdgeVectorLayer()
        qs = list(layer.get_queryset().values(*layer.tile_fields))
        self.assertEqual(len(qs), 1)
        # Without colors pool, default color from MAP_STYLES is used
        self.assertTrue(qs[0]["color"])

    def test_all_edge_vector_layers(self):
        layers = [
            LandEdgeVectorLayer(),
            CirculationEdgeVectorLayer(),
            CompetenceEdgeVectorLayer(),
            SignageManagementEdgeVectorLayer(),
            WorkManagementEdgeVectorLayer(),
        ]
        for layer in layers:
            qs = list(layer.get_queryset().values(*layer.tile_fields))
            self.assertEqual(len(qs), 1)
            self.assertTrue(qs[0]["color"])
