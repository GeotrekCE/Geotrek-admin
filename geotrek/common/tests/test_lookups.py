from django.test import TestCase

from geotrek.trekking.models import Trek
from geotrek.trekking.tests.factories import TrekFactory


class IsEmptyLookupTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.trek_with_geom = TrekFactory.create()

    def test_lookup_isempty_false(self):
        qs = Trek.objects.filter(geom__isempty=False)
        self.assertIn(self.trek_with_geom, qs)

    def test_lookup_isempty_true(self):
        qs = Trek.objects.filter(geom__isempty=True)
        self.assertNotIn(self.trek_with_geom, qs)
