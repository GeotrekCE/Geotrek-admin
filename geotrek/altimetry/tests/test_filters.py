from django.conf import settings
from django.test import TestCase

from geotrek.core.tests.factories import PathFactory
from geotrek.maintenance.filters import InterventionFilterSet
from geotrek.trekking.filters import POIFilterSet, TrekFilterSet
from geotrek.trekking.tests.factories import POIFactory, TrekFactory


class AltimetryFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path = PathFactory.create(
            geom="SRID=2154;LINESTRING(200000 300000, 1100000 1200000)"
        )
        if settings.TREKKING_TOPOLOGY_ENABLED:
            cls.trek = TrekFactory.create(paths=[cls.path], published=False)
            cls.poi = POIFactory.create(name="POI1", paths=[(cls.path, 0.5, 0.5)])
        else:
            cls.trek = TrekFactory.create(
                geom="SRID=2154;LINESTRING(200000 300000, 1100000 1200000)",
                published=False,
            )
            cls.poi = POIFactory.create(
                name="POI1", geom="SRID=2154;POINT (650000 750000)"
            )

    def test_filters_point(self):
        self.assertIn("elevation", POIFilterSet.get_filters())
        self.assertNotIn("length", POIFilterSet.get_filters())

    def test_filters_line(self):
        self.assertIn("elevation", TrekFilterSet.get_filters())
        self.assertIn("length", TrekFilterSet.get_filters())

    def test_filters_interventions(self):
        self.assertIn("elevation", InterventionFilterSet.get_filters())
        self.assertNotIn("length", InterventionFilterSet.get_filters())

    def test_filter_length_trek(self):
        filter = TrekFilterSet(data={"length_min": 10})
        self.assertIn(self.trek, filter.qs)
        self.assertEqual(len(filter.qs), 1)

        filter = TrekFilterSet(data={"length_max": 10})

        self.assertEqual(len(filter.qs), 0)

        filter = TrekFilterSet(data={"length_min": 10, "length_max": 1272793})

        self.assertIn(self.trek, filter.qs)
        self.assertEqual(len(filter.qs), 1)

    def test_filter_elevation_poi(self):
        filter = POIFilterSet(data={"elevation_min": 10})
        self.assertEqual(len(filter.qs), 0)

        filter = POIFilterSet(data={"elevation_max": 10})
        self.assertIn(self.poi, filter.qs)
        self.assertEqual(len(filter.qs), 1)

        filter = POIFilterSet(data={"elevation_min": 0, "elevation_max": 10})
        self.assertIn(self.poi, filter.qs)
        self.assertEqual(len(filter.qs), 1)
