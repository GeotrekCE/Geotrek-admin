from django_filters import CharFilter

from django.test import TestCase
from django.conf import settings

from mapentity.filters import TileFilter, PythonTileFilter, MapEntityFilterSet
from geotrek.diving.factories import DiveFactory
from geotrek.diving.models import Dive


class PolygonTest(object):

    def setUp(self):
        self.model = Dive
        self.none = DiveFactory.create(geom="POINT EMPTY")

        self.basic = DiveFactory.create(geom='SRID=%s;POLYGON((700000 6600000, 700000 6600003, 700003 6600003, 700003 6600000, 700000 6600000))' % settings.SRID)
        self.outside = DiveFactory.create(geom='SRID=%s;POLYGON((720200 6600200, 720200 6600800, 720800 6600800, 720800 6600200, 720200 6600200))' % settings.SRID)


class PythonTileFilterTest(PolygonTest, TestCase):

    def setUp(self):
        super(PythonTileFilterTest, self).setUp()
        self.filter = PythonTileFilter()

    def test_should_return_all_if_zoom_covers_france(self):
        tile_coords = '5/16/11'
        result = self.filter.filter(self.model.objects.all(), tile_coords)
        self.assertEqual(3, len(result))

    def test_should_include_null_geometry_in_search_results(self):
        tile_coords = '20/534597/372817'  # specific tiny tile with no data
        result = self.filter.filter(self.model.objects.all(), tile_coords)
        self.assertEqual(1, len(result))

    def test_should_filter_queryset_intersecting_tile(self):
        tile_coords = '10/521/362'
        result = self.filter.filter(self.model.objects.all(), tile_coords)
        self.assertEqual(2, len(result))


class TileFilterTest(PolygonTest, TestCase):

    def setUp(self):
        super(TileFilterTest, self).setUp()
        self.filter = TileFilter()

    def test_should_return_all_if_zoom_covers_france(self):
        tile_coords = '5/16/11'
        result = self.filter.filter(self.model.objects.all(), tile_coords)
        self.assertEqual(2, len(result))

    def test_should_not_include_null_or_empty_geometry_in_search_results(self):
        tile_coords = '20/534597/372817'  # specific tiny tile with no data
        result = self.filter.filter(self.model.objects.all(), tile_coords)
        self.assertEqual(0, len(result))

    def test_should_filter_queryset_intersecting_tile(self):
        tile_coords = '10/521/362'
        result = self.filter.filter(self.model.objects.all(), tile_coords)
        self.assertEqual(1, len(result))


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
