from django.http import QueryDict
from django.test import TestCase

from geotrek.outdoor.factories import SiteFactory, PracticeFactory
from geotrek.outdoor.filters import SiteFilterSet


class SiteFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.practice = PracticeFactory(name="Child practice", sector__name="Child sector")
        parent = SiteFactory.create(practice=None, name='Child site')
        SiteFactory.create(practice=cls.practice, parent=parent, name='Parent site')
        SiteFactory.create(name="Alone site")

    def test_practice_filter(self):
        filterset = SiteFilterSet(QueryDict('practice={}'.format(self.practice.pk)))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertQuerysetEqual(filterset.qs, ['<Site: Child site>', '<Site: Parent site>'])

    def test_sector_filter(self):
        filterset = SiteFilterSet(QueryDict('sector={}'.format(self.practice.sector.pk)))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertQuerysetEqual(filterset.qs, ['<Site: Child site>', '<Site: Parent site>'])

    # TODO: add orientation/wind filters
