from django.test import TestCase

from .. import factories


class CoreFactoriesTest(TestCase):
    """
    Ensure factories work as expected.
    Here we just call each one to ensure they do not trigger any random
    error without verifying any other expectation.
    """

    def test_path_factory(self):
        factories.PathFactory()

    def test_topology_mixin_factory(self):
        factories.TopologyFactory()

    def test_path_aggregation_factory(self):
        factories.PathAggregationFactory()

    def test_source_management_factory(self):
        factories.PathSourceFactory()

    def test_challenge_management_factory(self):
        factories.StakeFactory()

    def test_usage_management_factory(self):
        factories.UsageFactory()

    def test_network_management_factory(self):
        factories.NetworkFactory()

    def test_path_management_factory(self):
        factories.TrailFactory()
