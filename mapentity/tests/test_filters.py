from django_filters import CharFilter

from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry
from django.conf import settings

from mapentity.settings import API_SRID
from mapentity.filters import PythonPolygonFilter, MapEntityFilterSet
from geotrek.diving.factories import DiveFactory
from geotrek.diving.models import Dive


class PolygonTest:

    def test_should_return_all_if_filter_empty(self):
        result = self.filter.filter(self.model.objects.all(), None)
        self.assertEqual(3, len(result))

    def test_should_include_null_geometry_in_search_results(self):
        shape = GEOSGeometry('POLYGON((20 20, 40 20, 40 40, 20 40, 20 20))')
        result = self.filter.filter(self.model.objects.all(), shape)
        self.assertEqual(1, len(result))

    def test_should_consider_filter_shape_as_api_srid(self):
        shape = GEOSGeometry('POLYGON((-1 2, -1 4, 1 4, 1 2, -1 2))')
        result = self.filter.filter(self.model.objects.all(), shape)
        self.assertEqual(1, len(result))  # one of them is None

    def test_should_filter_queryset_intersecting_shape(self):
        shape = GEOSGeometry('POLYGON((0 -1, 4 -1, 4 1, 0 1, 0 -1))', srid=settings.SRID)
        shape.transform(API_SRID)
        result = self.filter.filter(self.model.objects.all(), shape)
        self.assertEqual(2, len(result))


"""
We will need to put it again when geom can be really nullable
class PolygonFilterTest(PolygonTest, TestCase):

    def setUp(self):
        self.model = Topology
        self.none = Topology.objects.create(geom=None)
        path = PathFactory.create(geom='SRID=%s;LINESTRING(0 0, 10 0, 10 10)' % settings.SRID)
        self.basic = TopologyFactory.create(paths=[(path, .1, .1)])
        self.outside = TopologyFactory.create(paths=[(path, .1, .1)])

        self.filter = PolygonFilter()
"""


class PythonPolygonFilterTest(PolygonTest, TestCase):

    def setUp(self):
        self.model = Dive
        self.none = DiveFactory.create(geom="POINT EMPTY")

        self.basic = DiveFactory.create(geom='SRID=%s;LINESTRING(0 0, 10 0)' % settings.SRID)
        self.outside = DiveFactory.create(geom='SRID=%s;LINESTRING(0 10, 10 10)' % settings.SRID)

        self.filter = PythonPolygonFilter()


class PluggableFilterSetTest(TestCase):

    def setUp(self):
        self.spot = DiveFactory.create(name="Empty")

        class DiveFilterSet(MapEntityFilterSet):
            class Meta:
                model = Dive
                fields = ()

        self.filterset_class = DiveFilterSet

    def test_empty_filter(self):
        filterset = self.filterset_class({'name': 'Foo'})
        self.assertEqual(filterset.qs.count(), 1)

    def test_add_filter_found(self):
        self.filterset_class.add_filter('name')
        filterset = self.filterset_class({'name': 'Empty'})
        self.assertEqual(filterset.qs.count(), 1)

    def test_add_filter_not_found(self):
        self.filterset_class.add_filter('name')
        filterset = self.filterset_class({'name': 'Foo'})
        self.assertEqual(filterset.qs.count(), 0)

    def test_add_filters_found(self):
        self.filterset_class.add_filters({'name': CharFilter()})
        filterset = self.filterset_class({'name': 'Empty'})
        self.assertEqual(filterset.qs.count(), 1)

    def test_add_filters_not_found(self):
        self.filterset_class.add_filters({'name': CharFilter()})
        filterset = self.filterset_class({'name': 'Foo'})
        self.assertEqual(filterset.qs.count(), 0)
