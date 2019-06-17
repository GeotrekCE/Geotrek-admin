from django.test import TestCase, tag

from .. import factories


class CoreFactoriesTest(TestCase):
    """
    Ensure factories work as expected.
    Here we just call each one to ensure they do not trigger any random
    error without verifying any other expectation.
    """

    @tag('dynamic_segmentation')
    def test_path_factory(self):
        factories.PathFactory()

    def test_topology_mixin_factory(self):
        factories.TopologyFactory()

    @tag('dynamic_segmentation')
    def test_path_aggregation_factory(self):
        factories.PathAggregationFactory()

    @tag('dynamic_segmentation')
    def test_source_management_factory(self):
        factories.PathSourceFactory()

    @tag('dynamic_segmentation')
    def test_challenge_management_factory(self):
        factories.StakeFactory()

    @tag('dynamic_segmentation')
    def test_usage_management_factory(self):
        factories.UsageFactory()

    @tag('dynamic_segmentation')
    def test_network_management_factory(self):
        factories.NetworkFactory()

    @tag('dynamic_segmentation')
    def test_path_management_factory(self):
        factories.TrailFactory()

    @tag('dynamic_segmentation')
    def test_path_in_bounds_existing_factory(self):
        factories.PathFactory.create()
        factories.PathInBoundsExistingGeomFactory()

    @tag('dynamic_segmentation')
    def test_path_in_bounds_not_existing_factory(self):
        with self.assertRaises(IndexError):
            factories.PathInBoundsExistingGeomFactory()
