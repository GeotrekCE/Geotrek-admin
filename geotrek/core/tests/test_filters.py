from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from django.test import TestCase

from geotrek.authent.tests.factories import StructureFactory
from geotrek.core.filters import PathFilterSet, TopologyFilter, TrailFilterSet
from geotrek.core.models import Topology
from geotrek.land.tests.test_filters import LandFiltersTest
from geotrek.trekking.filters import TrekFilterSet
from geotrek.trekking.tests.factories import TrekFactory

from .factories import (
    CertificationLabelFactory,
    CertificationTrailFactory,
    PathFactory,
    TrailFactory,
)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class PathFilterLandTest(LandFiltersTest):
    filterclass = PathFilterSet


class TestFilter(TopologyFilter):
    model = Topology


class TopologyFilterTest(TestCase):
    def test_values_to_edges(self):
        topology = TestFilter()

        with self.assertRaises(NotImplementedError):
            topology.values_to_edges(['Value'])


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class TopologyFilterTrailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path = PathFactory()
        cls.trail = TrailFactory(paths=[(cls.path, 0, 1)])

    def test_trail_filters(self):
        PathFactory()
        qs = PathFilterSet().qs
        self.assertEqual(qs.count(), 2)

        data = {'trail': [self.trail]}
        qs = PathFilterSet(data=data).qs
        self.assertEqual(qs.count(), 1)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class ValidTopologyFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path = PathFactory()
        cls.trek = TrekFactory.create(name="Crossed", paths=[(cls.path, 0, 1)])

    def test_trek_filters_not_valid(self):
        trek = TrekFactory.create(name="Not crossed", paths=[(self.path, 0, 0.5)])
        TrekFactory.create(paths=[])
        qs = TrekFilterSet().qs
        self.assertEqual(qs.count(), 3)

        data = {'is_valid_topology': True}
        qs = TrekFilterSet(data=data).qs
        self.assertIn(self.trek, qs)
        self.assertEqual(qs.count(), 2)

        data = {'is_valid_topology': False}
        qs = TrekFilterSet(data=data).qs
        self.assertEqual(qs.count(), 1)

        geom = LineString(Point(700100, 6600000), Point(700000, 6600100), srid=settings.SRID)
        PathFactory.create(geom=geom)
        self.trek.reload()
        trek.reload()
        data = {'is_valid_topology': True}
        qs = TrekFilterSet(data=data).qs
        self.assertNotIn(self.trek, qs)
        self.assertIn(trek, qs)
        self.assertEqual(qs.count(), 1)

        data = {'is_valid_topology': False}
        qs = TrekFilterSet(data=data).qs
        self.assertIn(self.trek, qs)
        self.assertNotIn(trek, qs)
        self.assertEqual(qs.count(), 2)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class ValidGeometryFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path = PathFactory()

    def test_trek_filters_not_valid_geometry(self):
        trek_linestring = TrekFactory.create(name="LineString", paths=[(self.path, 0, 1)])
        trek_multilinestring = TrekFactory.create(name="Multilinestring", paths=[(self.path, 0, 0.4, 1),
                                                                                 (self.path, 0.6, 1, 2)])
        trek_point = TrekFactory.create(name="Point", paths=[(self.path, 0, 0)])
        trek_none = TrekFactory.create(name="None", paths=[])

        qs = TrekFilterSet().qs
        self.assertEqual(qs.count(), 4)

        data = {'is_valid_geometry': True}
        qs = TrekFilterSet(data=data).qs
        self.assertIn(trek_linestring, qs)
        self.assertEqual(qs.count(), 1)

        data = {'is_valid_geometry': False}
        qs = TrekFilterSet(data=data).qs
        self.assertIn(trek_multilinestring, qs)
        self.assertIn(trek_point, qs)
        self.assertIn(trek_none, qs)
        self.assertEqual(qs.count(), 3)


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
class ValidGeometryFilterNDSTest(TestCase):
    def test_trek_filters_not_valid_geometry_nds(self):
        trek_empty = TrekFactory.create(name="Empty", geom='SRID=2154;LINESTRING EMPTY')
        trek_valid = TrekFactory.create(name="Valid", geom=LineString((0, 0), (5, 5)))
        qs = TrekFilterSet().qs
        self.assertEqual(qs.count(), 2)

        data = {'is_valid_geometry': True}
        qs = TrekFilterSet(data=data).qs
        self.assertIn(trek_valid, qs)
        self.assertEqual(qs.count(), 1)

        data = {'is_valid_geometry': False}
        qs = TrekFilterSet(data=data).qs
        self.assertIn(trek_empty, qs)
        self.assertEqual(qs.count(), 1)


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
            trail=self.trail1,
            certification_label=self.certification_label_1
        )
        self.certification_trail_2 = CertificationTrailFactory.create(
            trail=self.trail2,
            certification_label=self.certification_label_2
        )
        self.filterset_class = TrailFilterSet

    def test_filter_trail_on_certification_label(self):
        """Test trail filter on certification label"""
        filterset = self.filterset_class({'certification_labels': [self.certification_label_1]})
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
        path1 = PathFactory.create(provider='my_provider1')
        path2 = PathFactory.create(provider='my_provider2')

        filter_set = PathFilterSet()
        filter_form = filter_set.form

        self.assertIn('<option value="my_provider1">my_provider1</option>', filter_form.as_p())
        self.assertIn('<option value="my_provider2">my_provider2</option>', filter_form.as_p())

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
        trail1 = TrailFactory.create(provider='my_provider1')
        trail2 = TrailFactory.create(provider='my_provider2')

        filter_set = TrailFilterSet()
        filter_form = filter_set.form

        self.assertIn('<option value="my_provider1">my_provider1</option>', filter_form.as_p())
        self.assertIn('<option value="my_provider2">my_provider2</option>', filter_form.as_p())

        self.assertIn(trail1, filter_set.qs)
        self.assertIn(trail2, filter_set.qs)
