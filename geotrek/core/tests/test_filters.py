from unittest import skipIf

from django.conf import settings
from django.test import TestCase

from geotrek.authent.tests.factories import StructureFactory
from geotrek.common.models import Provider
from geotrek.core.filters import PathFilterSet, TopologyFilter, TrailFilterSet, \
    ValidTopologyFilterSet
from geotrek.core.models import Topology, PathAggregation
from geotrek.land.tests.test_filters import LandFiltersTest
from geotrek.trekking.filters import TrekFilterSet, POIFilterSet
from geotrek.trekking.tests.factories import TrekFactory, POIFactory

from .factories import (
    CertificationLabelFactory,
    CertificationTrailFactory,
    PathFactory,
    TrailFactory, TopologyFactory,
)
from geotrek.common.tests.utils import LineStringInBounds, PointInBounds


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class PathFilterLandTest(LandFiltersTest):
    filterclass = PathFilterSet


class TestFilter(TopologyFilter):
    model = Topology


class TopologyFilterTest(TestCase):
    def test_values_to_edges(self):
        topology = TestFilter()

        with self.assertRaises(NotImplementedError):
            topology.values_to_edges(["Value"])


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class TopologyFilterTrailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path = PathFactory()
        cls.trail = TrailFactory(paths=[(cls.path, 0, 1)])

    def test_trail_filters(self):
        PathFactory()
        qs = PathFilterSet().qs
        self.assertEqual(qs.count(), 2)

        data = {"trail": [self.trail]}
        qs = PathFilterSet(data=data).qs
        self.assertEqual(qs.count(), 1)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class ValidTopologyFilterTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
            All 3 paths are snapped.

                                   path3
                             ┍━━━━━━━>━━━━━━━━
                             │
                             │
                             │
                             ^ path2
                             │
                             │
            ━━━━━━━━>━━━━━━━━┙
                  path1
        """
        cls.path1 = PathFactory(geom=LineStringInBounds((0, 0), (10, 0)))
        cls.path2 = PathFactory(geom=LineStringInBounds((10, 0), (10, 10)))
        cls.path3 = PathFactory(geom=LineStringInBounds((10, 10), (10, 20)))

    def test_valid_topology_no_aggregations(self):
        """Topologies with path aggregations should be considered valid."""
        poi = POIFactory.create(name="POI", geom=PointInBounds(5, 0))
        trek = TrekFactory.create(name="Trek", paths=[(self.path1, 0, 1)])
        PathAggregation.objects.all().delete()

        # Both of these topologies should be considered valid
        valid_poi_qs = POIFilterSet(data={"is_valid_topology": True}).qs
        invalid_poi_qs = POIFilterSet(data={"is_valid_topology": False}).qs
        self.assertEqual(valid_poi_qs.count(), 1)
        self.assertEqual(invalid_poi_qs.count(), 0)

        valid_trek_qs = TrekFilterSet(data={"is_valid_topology": True}).qs
        invalid_trek_qs = TrekFilterSet(data={"is_valid_topology": False}).qs
        self.assertEqual(valid_trek_qs.count(), 1)
        self.assertEqual(invalid_trek_qs.count(), 0)

    def test_valid_topology_point(self):
        """Point topologies with no offset inconsistencies should be considered valid."""
        POIFactory.create(name="POI on a path", geom=PointInBounds(5, 0))
        POIFactory.create(name="POI not on a path", geom=PointInBounds(5, 5))
        POIFactory.create(name="POI on an intersection", geom=PointInBounds(10, 0))

        # All these topologies should be considered valid
        valid_qs = POIFilterSet(data={"is_valid_topology": True}).qs
        invalid_qs = POIFilterSet(data={"is_valid_topology": False}).qs
        self.assertEqual(valid_qs.count(), 3)
        self.assertEqual(invalid_qs.count(), 0)

    def test_valid_topology_linear_on_one_path(self):
        """Valid linear topologies which go through one path only."""

        TrekFactory.create(name="Whole path, no waypoint", paths=[(self.path1, 0, 1)])
        TrekFactory.create(name="Fraction of path, no waypoint", paths=[(self.path1, 0.3, 0.7)])
        TrekFactory.create(name="Whole path, no waypoint, reverse direction", paths=[(self.path1, 1, 0)])
        TrekFactory.create(name="Fraction of path, no waypoint, reverse direction", paths=[(self.path1, 0.7, 0.3)])
        TrekFactory.create(
            name="Fraction of path, two waypoints",
            paths=[
                (self.path1, 0.3, 0.5),
                (self.path1, 0.5, 0.5),  # Waypoint
                (self.path1, 0.5, 0.7),
                (self.path1, 0.7, 0.7),  # Waypoint
                (self.path1, 0.7, 1),
            ]
        )
        TrekFactory.create(
            name="Fraction of path, two waypoints, reverse direction",
            paths=[
                (self.path1, 1, 0.7),
                (self.path1, 0.7, 0.7),  # Waypoint
                (self.path1, 0.7, 0.5),
                (self.path1, 0.5, 0.5),  # Waypoint
                (self.path1, 0.5, 0.3),
            ]
        )

        # All these topologies should be considered valid
        valid_qs = TrekFilterSet(data={"is_valid_topology": True}).qs
        invalid_qs = TrekFilterSet(data={"is_valid_topology": False}).qs
        self.assertEqual(valid_qs.count(), 6)
        self.assertEqual(invalid_qs.count(), 0)

    def test_valid_topology_linear_on_three_same_direction_paths(self):
        """Valid linear topologies which go through several same-direction paths."""

        TrekFactory.create(
            name="Whole paths, no waypoint",
            paths=[(self.path1, 0, 1), (self.path2, 0, 1), (self.path3, 0, 1)]
        )
        TrekFactory.create(
            name="Three waypoints",
            paths=[
                (self.path1, 0, 0.5),
                (self.path1, 0.5, 0.5),  # Waypoint
                (self.path1, 0.5, 1),
                (self.path2, 0, 1),
                (self.path3, 0, 0),  # Waypoint at start of path3
                (self.path3, 0, 0.5),
                (self.path3, 0.5, 0.5),  # Waypoint
                (self.path3, 0.5, 0.7),
            ]
        )

        # Both of these topologies should be considered valid
        valid_qs = TrekFilterSet(data={"is_valid_topology": True}).qs
        invalid_qs = TrekFilterSet(data={"is_valid_topology": False}).qs
        self.assertEqual(valid_qs.count(), 2)
        self.assertEqual(invalid_qs.count(), 0)

    def test_valid_topology_linear_on_three_mixed_direction_paths(self):
        """Valid linear topologies which go through several mixed-direction paths."""

        self.path2.reverse()
        self.path2.save()
        TrekFactory.create(
            name="Whole paths, no waypoint",
            paths=[(self.path1, 0, 1), (self.path2, 1, 0), (self.path3, 0, 1)]
        )
        TrekFactory.create(
            name="Whole paths, two waypoints",
            paths=[
                (self.path1, 0, 1),
                (self.path2, 1, 0.5),
                (self.path2, 0.5, 0.5),  # Waypoint
                (self.path2, 0.5, 0),
                (self.path3, 0, 0.5),
                (self.path3, 0.5, 0.5),  # Waypoint
                (self.path3, 0.5, 1),
            ]
        )

        # Both of these topologies should be considered valid
        valid_qs = TrekFilterSet(data={"is_valid_topology": True}).qs
        invalid_qs = TrekFilterSet(data={"is_valid_topology": False}).qs
        self.assertEqual(valid_qs.count(), 2)
        self.assertEqual(invalid_qs.count(), 0)

    def test_invalid_topology_duplicate_orders(self):
        """Topologies with duplicate order values across their path aggregations should be considered invalid."""

        # This trek goes through the entirety of path1 and has one waypoint.
        # Its path aggregations orders is 0, 0, 1 instead of 0, 1, 2
        trek_one_whole_path_one_waypoint = TrekFactory.create(name="Trek 1")
        trek_one_whole_path_one_waypoint.add_path(self.path1, start=0, end=0.5, order=0, reload=False)
        trek_one_whole_path_one_waypoint.add_path(self.path1, start=0.5, end=0.5, order=0, reload=False)  # Waypoint
        trek_one_whole_path_one_waypoint.add_path(self.path1, start=0.5, end=1, order=1)

        # This trek goes through the entirety of path1 in reverse and has one waypoint.
        # Its path aggregations orders is 0, 0, 1 instead of 0, 1, 2
        trek_one_whole_path_reverse_one_waypoint = TrekFactory.create(name="Trek 2")
        trek_one_whole_path_reverse_one_waypoint.add_path(self.path1, start=1, end=0.5, order=0, reload=False)
        trek_one_whole_path_reverse_one_waypoint.add_path(self.path1, start=0.5, end=0.5, order=0, reload=False)  # Waypoint
        trek_one_whole_path_reverse_one_waypoint.add_path(self.path1, start=0.5, end=0, order=1)

        # This trek goes through a portion of path1 and has one waypoint.
        # Its path aggregations orders is 0, 0, 1 instead of 0, 1, 2
        trek_one_path_portion_one_waypoint = TrekFactory.create(name="Trek 3")
        trek_one_path_portion_one_waypoint.add_path(self.path1, start=0.1, end=0.5, order=0, reload=False)
        trek_one_path_portion_one_waypoint.add_path(self.path1, start=0.5, end=0.5, order=0, reload=False)  # Waypoint
        trek_one_path_portion_one_waypoint.add_path(self.path1, start=0.5, end=0.9, order=1)

        # This trek goes through the entirety of path1 and has two waypoints.
        # Its path aggregations orders is 0, 1, 2, 3, 1 instead of 0, 1, 2, 3, 4
        trek_one_whole_path_two_waypoints = TrekFactory.create(name="Trek 4")
        trek_one_whole_path_two_waypoints.add_path(self.path1, start=0, end=0.3, order=0, reload=False)
        trek_one_whole_path_two_waypoints.add_path(self.path1, start=0.3, end=0.3, order=1, reload=False)  # Waypoint
        trek_one_whole_path_two_waypoints.add_path(self.path1, start=0.3, end=0.7, order=2, reload=False)
        trek_one_whole_path_two_waypoints.add_path(self.path1, start=0.7, end=0.7, order=3, reload=False)  # Waypoint
        trek_one_whole_path_two_waypoints.add_path(self.path1, start=0.7, end=1, order=1)

        # This trek goes through the entirety of paths 1, 2 and 3 and has no waypoint.
        # Its path aggregations orders is 0, 1, 0 instead of 0, 1, 2
        trek_three_whole_paths_no_waypoint = TrekFactory.create(name="Trek 5")
        trek_three_whole_paths_no_waypoint.add_path(self.path1, start=0, end=1, order=0, reload=False)
        trek_three_whole_paths_no_waypoint.add_path(self.path1, start=0, end=1, order=1, reload=False)
        trek_three_whole_paths_no_waypoint.add_path(self.path1, start=0, end=1, order=0)

        # All these topologies should be considered invalid
        valid_qs = TrekFilterSet(data={"is_valid_topology": True}).qs
        invalid_qs = TrekFilterSet(data={"is_valid_topology": False}).qs
        self.assertEqual(valid_qs.count(), 0)
        self.assertEqual(invalid_qs.count(), 5)

    def test_invalid_topology_incorrect_order(self):
        """Topologies with incorrect order values across their path aggregations should be considered invalid."""

        # This trek goes through path1 and has one waypoint.
        # Its path aggregations orders is 0, 2, 1 instead of 0, 1, 2.
        trek_one_path_one_waypoint_wrong_order = TrekFactory.create(name="Trek 1")
        trek_one_path_one_waypoint_wrong_order.add_path(self.path1, start=0, end=0.5, order=0, reload=False)
        trek_one_path_one_waypoint_wrong_order.add_path(self.path1, start=0.5, end=0.5, order=2, reload=False)  # Waypoint
        trek_one_path_one_waypoint_wrong_order.add_path(self.path1, start=0.5, end=1, order=1)

        # This trek goes through path1 and has one waypoint.
        # Its path aggregations orders is 0, 2, 3 instead of 0, 1, 2.
        trek_one_path_one_waypoint_missing_order = TrekFactory.create(name="Trek 2")
        trek_one_path_one_waypoint_missing_order.add_path(self.path1, start=0, end=0.5, order=0, reload=False)
        trek_one_path_one_waypoint_missing_order.add_path(self.path1, start=0.5, end=0.5, order=2, reload=False)  # Waypoint
        trek_one_path_one_waypoint_missing_order.add_path(self.path1, start=0.5, end=1, order=3)

        # This trek goes through path1 and has one waypoint.
        # Its path aggregations orders is 1, 2, 3 instead of 0, 1, 2.
        trek_one_path_one_waypoint_wrong_start = TrekFactory.create(name="Trek 3")
        trek_one_path_one_waypoint_wrong_start.add_path(self.path1, start=0, end=0.5, order=1, reload=False)
        trek_one_path_one_waypoint_wrong_start.add_path(self.path1, start=0.5, end=0.5, order=2, reload=False)  # Waypoint
        trek_one_path_one_waypoint_wrong_start.add_path(self.path1, start=0.5, end=1, order=3)

        # This trek goes through path1 and path2 with no waypoint.
        # Its path aggregations orders is 1, 0 instead of 0, 1.
        trek_two_paths_wrong_order = TrekFactory.create(name="Trek 4")
        trek_two_paths_wrong_order.add_path(self.path1, start=0, end=1, order=1, reload=False)
        trek_two_paths_wrong_order.add_path(self.path2, start=0, end=1, order=0)

        # This trek goes through path1, path2 and path3 with no waypoint.
        # Its path aggregations orders is 1, 2, 0 instead of 0, 1, 2.
        trek_three_paths_wrong_order = TrekFactory.create(name="Trek 5")
        trek_three_paths_wrong_order.add_path(self.path1, start=0, end=1, order=1, reload=False)
        trek_three_paths_wrong_order.add_path(self.path2, start=0, end=1, order=2, reload=False)
        trek_three_paths_wrong_order.add_path(self.path3, start=0, end=1, order=0)

        # All these topologies should be considered invalid
        valid_qs = TrekFilterSet(data={"is_valid_topology": True}).qs
        invalid_qs = TrekFilterSet(data={"is_valid_topology": False}).qs
        self.assertEqual(valid_qs.count(), 0)
        self.assertEqual(invalid_qs.count(), 5)

    def test_invalid_topology_wrong_direction(self):
        """Topologies with path aggregations going into the wrong direction should be considered invalid."""

        # This trek goes through path1, path2 and path3 with no waypoint.
        # The path aggregation for path2 has the wrong direction (1 to 0).
        trek_three_paths_no_waypoint = TrekFactory.create(name="Trek 1")
        trek_three_paths_no_waypoint.add_path(self.path1, start=0, end=1, order=0, reload=False)
        trek_three_paths_no_waypoint.add_path(self.path2, start=1, end=0, order=1, reload=False)
        trek_three_paths_no_waypoint.add_path(self.path3, start=0, end=1, order=2)

        # This topology should be considered invalid
        valid_qs = TrekFilterSet(data={"is_valid_topology": True}).qs
        invalid_qs = TrekFilterSet(data={"is_valid_topology": False}).qs
        self.assertEqual(valid_qs.count(), 0)
        self.assertEqual(invalid_qs.count(), 1)

    def test_invalid_topology_gap(self):
        """Topologies with gaps between their path aggregations should be considered invalid."""

        # This trek goes through path1 and has one waypoint.
        # There is a gap between the waypoint (0.5) and the next aggregation (0.7).
        trek_one_path_one_waypoint = TrekFactory.create(name="Trek 1")
        trek_one_path_one_waypoint.add_path(self.path1, start=0, end=0.5, order=0, reload=False)
        trek_one_path_one_waypoint.add_path(self.path1, start=0.5, end=0.5, order=1, reload=False)  # Waypoint
        trek_one_path_one_waypoint.add_path(self.path1, start=0.7, end=1, order=2)

        # This trek goes through path1 in reverse and has one waypoint.
        # There is a gap between the waypoint (0.5) and the next aggregation (0.3).
        trek_one_path_one_waypoint_reverse = TrekFactory.create(name="Trek 2")
        trek_one_path_one_waypoint_reverse.add_path(self.path1, start=1, end=0.5, order=0, reload=False)
        trek_one_path_one_waypoint_reverse.add_path(self.path1, start=0.5, end=0.5, order=1, reload=False)  # Waypoint
        trek_one_path_one_waypoint_reverse.add_path(self.path1, start=0.3, end=0, order=2)

        # This trek goes through a portion of path1 and then a portion of path2.
        # There is a gap between the end of path1's covered portion and the start of path2's covered portion.
        trek_two_paths_touching = TrekFactory.create(name="Trek 3")
        trek_two_paths_touching.add_path(self.path1, start=0, end=0.5, order=0, reload=False)
        trek_two_paths_touching.add_path(self.path2, start=0.5, end=1, order=1)

        # This trek goes through a portion of path2 and then a portion of path1, in reverse.
        # There is a gap between the end of path2's covered portion and the start of path1's covered portion.
        trek_two_paths_touching_reverse = TrekFactory.create(name="Trek 4")
        trek_two_paths_touching_reverse.add_path(self.path2, start=1, end=0.5, order=0, reload=False)
        trek_two_paths_touching_reverse.add_path(self.path1, start=0.5, end=0, order=1)

        # This trek goes through the entirety of path1 and then path3
        # Paths 1 and 3 are not geometrically connected, which creates a gap in the topology
        trek_two_paths_not_touching = TrekFactory.create(name="Trek 5")
        trek_two_paths_not_touching.add_path(self.path1, start=0, end=1, order=0, reload=False)
        trek_two_paths_not_touching.add_path(self.path3, start=0, end=1, order=1)

        # This trek goes through the entirety of path3 and then path1, in reverse
        # Paths 1 and 3 are not geometrically connected, which creates a gap in the topology
        trek_two_paths_not_touching_reverse = TrekFactory.create(name="Trek 6")
        trek_two_paths_not_touching_reverse.add_path(self.path3, start=1, end=0, order=0, reload=False)
        trek_two_paths_not_touching_reverse.add_path(self.path1, start=1, end=0, order=1)

        # All these topologies should be considered invalid
        valid_qs = TrekFilterSet(data={"is_valid_topology": True}).qs
        invalid_qs = TrekFilterSet(data={"is_valid_topology": False}).qs
        self.assertEqual(valid_qs.count(), 0)
        self.assertEqual(invalid_qs.count(), 6)

    def test_invalid_topology_overlap(self):
        """Topologies with overlapping path aggregations should be considered invalid."""

        # This trek goes through path1 and has one waypoint.
        # There is an overlap between the first aggregation (0-0.7) and the last aggregation (0.3-1).
        trek_one_path_one_waypoint = TrekFactory.create(name="Trek 1")
        trek_one_path_one_waypoint.add_path(self.path1, start=0, end=0.7, order=0, reload=False)
        trek_one_path_one_waypoint.add_path(self.path1, start=0.7, end=0.7, order=1, reload=False)  # Waypoint
        trek_one_path_one_waypoint.add_path(self.path1, start=0.3, end=1, order=2)

        # This trek goes through path1 in reverse and has one waypoint.
        # There is an overlap between the first aggregation (1-0.3) and the last aggregation (0.7-0).
        trek_one_path_one_waypoint_reverse = TrekFactory.create(name="Trek 2")
        trek_one_path_one_waypoint_reverse.add_path(self.path1, start=1, end=0.3, order=0, reload=False)
        trek_one_path_one_waypoint_reverse.add_path(self.path1, start=0.7, end=0.7, order=1, reload=False)  # Waypoint
        trek_one_path_one_waypoint_reverse.add_path(self.path1, start=0.7, end=0, order=2)

        # All these topologies should be considered invalid
        valid_qs = TrekFilterSet(data={"is_valid_topology": True}).qs
        invalid_qs = TrekFilterSet(data={"is_valid_topology": False}).qs
        self.assertEqual(valid_qs.count(), 0)
        self.assertEqual(invalid_qs.count(), 2)

    def test_invalid_topology_not_a_subclass(self):
        """
        This FilterSet should be usable both with the Topology class and its subclasses.
        Previous test cases check that it works with POIs and Treks. This one uses Topology objects.
        """
        valid_point_topology = TopologyFactory.create(geom=PointInBounds(5, 5))

        # This linear topology is invalid.
        # It has a duplicate order across its path aggregations (0, 0, 2 instead of 0, 1, 2)
        invalid_linear_topology = TopologyFactory.create()
        invalid_linear_topology.add_path(self.path1, start=0, end=0.5, order=0, reload=False)
        invalid_linear_topology.add_path(self.path1, start=0.5, end=0.5, order=0, reload=False)  # Waypoint
        invalid_linear_topology.add_path(self.path1, start=0.5, end=1, order=2)

        # The first topology should be considered valid, and the second one should be considered invalid.
        valid_qs = ValidTopologyFilterSet(data={"is_valid_topology": True}).qs
        invalid_qs = ValidTopologyFilterSet(data={"is_valid_topology": False}).qs
        self.assertEqual(valid_qs.count(), 1)
        self.assertEqual(valid_qs.first(), valid_point_topology)
        self.assertEqual(invalid_qs.count(), 1)
        self.assertEqual(invalid_qs.first(), invalid_linear_topology)


    # TODO: Malformed (two aggregations on the same path with no waypoint)
    # - implement the check
    # - change the comments
    # - change the variable names
    # - add cases:
    #     - sub-topo (path1, path2, path1)
    #     - sub-topo (path1, path2, path2, path3)
    #     - reverse for each of them
    #     - or maybe remove some cases because if we're checking for repeated paths, checking is easier (overlap is less/not important)

    # def test_invalid_topology_repeated_path(self):
    #     """TODO"""
    #
    #     # This trek goes through path1 with no waypoint.
    #     # The first aggregation (0-0.7) overlaps the second aggregation (0.3-1).
    #     foo = TrekFactory.create(name="Trek 3")
    #     foo.add_path(self.path1, start=0, end=0.7, order=0)
    #     foo.add_path(self.path1, start=0.3, end=1, order=1)
    #
    #     # This trek goes through path1 in reverse with no waypoint.
    #     # The first aggregation (1-0.3) overlaps the start of the second aggregation (0.7-0).
    #     bar = TrekFactory.create(name="Trek 4")
    #     bar.add_path(self.path1, start=1, end=0.3, order=0)
    #     bar.add_path(self.path1, start=0.7, end=0, order=1)
    #
    #     # This trek goes through path1 twice with no waypoint.
    #     # Both aggregations have the same start and end points.
    #     wow = TrekFactory.create(name="Trek 5")
    #     wow.add_path(self.path1, start=0, end=1, order=0)
    #     wow.add_path(self.path1, start=0, end=1, order=1)
    #
    #     # This trek goes through path1 twice in reverse with no waypoint.
    #     # Both aggregations have the same start and end points.
    #     azerty = TrekFactory.create(name="Trek 6")
    #     azerty.add_path(self.path1, start=1, end=0, order=0)
    #     azerty.add_path(self.path1, start=1, end=0, order=1)
    #
    #     # This trek goes through path1 with no waypoint.
    #     # The second aggregation (0.3-0.7) is fully contained within the first aggregation (0-1).
    #     blip = TrekFactory.create(name="Trek 7")
    #     blip.add_path(self.path1, start=0, end=1, order=0)
    #     blip.add_path(self.path1, start=0.3, end=0.7, order=1)
    #
    #     # This trek goes through path1 in reverse with no waypoint.
    #     # The second aggregation (0.7-0.3) is fully contained within the first aggregation (1-0).
    #     bloup = TrekFactory.create(name="Trek 8")
    #     bloup.add_path(self.path1, start=1, end=0, order=0)
    #     bloup.add_path(self.path1, start=0.7, end=0.3, order=1)



class TrailFilterTestCase(TestCase):
    """Test trail filters"""

    def setUp(self):
        self.structure = StructureFactory.create(name="structure")
        self.trail1 = TrailFactory.create(
            structure=self.structure,
        )
        self.trail2 = TrailFactory.create(
            structure=self.structure,
        )
        self.certification_label_1 = CertificationLabelFactory.create()
        self.certification_label_2 = CertificationLabelFactory.create()
        self.certification_trail_1 = CertificationTrailFactory.create(
            trail=self.trail1, certification_label=self.certification_label_1
        )
        self.certification_trail_2 = CertificationTrailFactory.create(
            trail=self.trail2, certification_label=self.certification_label_2
        )
        self.filterset_class = TrailFilterSet

    def test_filter_trail_on_certification_label(self):
        """Test trail filter on certification label"""
        filterset = self.filterset_class(
            {"certification_labels": [self.certification_label_1]}
        )
        self.assertEqual(filterset.qs.count(), 1)


class PathFilterTest(TestCase):
    factory = PathFactory
    filterset = PathFilterSet

    def test_provider_filter_without_provider(self):
        filter_set = PathFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(0, filter_set.qs.count())

    def test_provider_filter_with_providers(self):
        provider1 = Provider.objects.create(name="Provider1")
        provider2 = Provider.objects.create(name="Provider2")
        path1 = PathFactory.create(provider=provider1)
        path2 = PathFactory.create(provider=provider2)

        filter_set = PathFilterSet()
        filter_form = filter_set.form

        self.assertIn(
            f'<option value="{provider1.pk}">Provider1</option>', filter_form.as_p()
        )
        self.assertIn(
            f'<option value="{provider2.pk}">Provider2</option>', filter_form.as_p()
        )

        self.assertIn(path1, filter_set.qs)
        self.assertIn(path2, filter_set.qs)


class TrailFilterTest(TestCase):
    factory = TrailFactory
    filterset = TrailFilterSet

    def test_provider_filter_without_provider(self):
        filter_set = TrailFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(0, filter_set.qs.count())

    def test_provider_filter_with_providers(self):
        provider1 = Provider.objects.create(name="Provider1")
        provider2 = Provider.objects.create(name="Provider2")
        trail1 = TrailFactory.create(provider=provider1)
        trail2 = TrailFactory.create(provider=provider2)

        filter_set = TrailFilterSet()
        filter_form = filter_set.form

        self.assertIn(
            f'<option value="{provider1.pk}">Provider1</option>', filter_form.as_p()
        )
        self.assertIn(
            f'<option value="{provider2.pk}">Provider2</option>', filter_form.as_p()
        )

        self.assertIn(trail1, filter_set.qs)
        self.assertIn(trail2, filter_set.qs)
