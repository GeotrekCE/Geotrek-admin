from django.test import TestCase
from django.conf import settings
from django.test.utils import override_settings

from geotrek.core import factories as core_factories
from geotrek.tourism import factories as tourism_factories
from geotrek.trekking import factories as trekking_factories


class TourismRelations(TestCase):

    def setUp(self):
        self.content = tourism_factories.TouristicContentFactory(geom='SRID=%s;POINT(1 1)' % settings.SRID)
        self.content2 = tourism_factories.TouristicContentFactory(geom='SRID=%s;POINT(2 2)' % settings.SRID)
        self.event = tourism_factories.TouristicEventFactory(geom='SRID=%s;POINT(50 50)' % settings.SRID)
        self.event2 = tourism_factories.TouristicEventFactory(geom='SRID=%s;POINT(60 60)' % settings.SRID)
        path = core_factories.PathFactory(geom='SRID=%s;LINESTRING(0 100, 100 100)' % settings.SRID)
        self.trek = trekking_factories.TrekFactory(no_path=True)
        self.trek.add_path(path)
        self.poi = trekking_factories.POIFactory(no_path=True)
        self.poi.add_path(path, start=0.5, end=0.5)

    def test_spatial_link_with_tourism(self):
        self.assertIn(self.content2, self.content.touristic_contents.all())
        self.assertIn(self.event, self.content.touristic_events.all())
        self.assertIn(self.content, self.event.touristic_contents.all())
        self.assertIn(self.event2, self.event.touristic_events.all())

    def test_spatial_links_do_not_self_intersect(self):
        self.assertNotIn(self.content, self.content.touristic_contents.all())
        self.assertNotIn(self.event, self.event.touristic_contents.all())

    @override_settings(TOURISM_INTERSECTION_MARGIN=10)
    def test_spatial_link_with_tourism_respects_limit(self):
        self.assertNotIn(self.event, self.content.touristic_events.all())
        self.assertNotIn(self.content, self.event.touristic_contents.all())

    def test_spatial_link_with_topologies(self):
        self.assertIn(self.trek, self.content.treks.all())
        self.assertIn(self.poi, self.content.pois.all())
        self.assertIn(self.trek, self.event.treks.all())
        self.assertIn(self.poi, self.event.pois.all())

    @override_settings(TOURISM_INTERSECTION_MARGIN=10)
    def test_spatial_link_with_topologies_respects_limit(self):
        self.assertNotIn(self.trek, self.content.treks.all())
        self.assertNotIn(self.poi, self.content.pois.all())
        self.assertNotIn(self.trek, self.event.treks.all())
        self.assertNotIn(self.poi, self.event.pois.all())

    def test_spatial_link_from_topologies(self):
        self.assertIn(self.content, self.trek.touristic_contents.all())
        self.assertIn(self.content, self.poi.touristic_contents.all())
        self.assertIn(self.event, self.trek.touristic_events.all())
        self.assertIn(self.event, self.poi.touristic_events.all())

    @override_settings(TOURISM_INTERSECTION_MARGIN=10)
    def test_spatial_link_from_topologies_respects_limit(self):
        self.assertNotIn(self.content, self.trek.touristic_contents.all())
        self.assertNotIn(self.content, self.poi.touristic_contents.all())
        self.assertNotIn(self.event, self.trek.touristic_events.all())
        self.assertNotIn(self.event, self.poi.touristic_events.all())

    def test_spatial_link_from_trek_with_practice_distance(self):
        self.trek.practice.distance = 2000
        self.trek.practice.save()
        self.assertIn(self.content, self.trek.touristic_contents.all())
        self.assertIn(self.event, self.trek.touristic_events.all())

    def test_spatial_link_from_trek_with_practice_distance_respects_limit(self):
        self.trek.practice.distance = 10
        self.trek.practice.save()
        self.assertNotIn(self.content, self.trek.touristic_contents.all())
        self.assertNotIn(self.event, self.trek.touristic_events.all())
