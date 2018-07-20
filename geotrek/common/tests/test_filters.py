from django.test import TestCase

from geotrek.maintenance.factories import ProjectFactory
from geotrek.maintenance.filters import ProjectFilterSet


class ProjectYearsFilterTest(TestCase):
    def setUp(self):
        ProjectFactory.create(begin_year=1500, end_year=2000)
        ProjectFactory.create(begin_year=1700, end_year=1800)
        self.filter = ProjectFilterSet()
        self.widget = self.filter.filters['in_year'].field.widget

    def test_filter_year_with_string(self):
        filter = ProjectFilterSet(data={'in_year': 'toto'})
        p = ProjectFactory.create(begin_year=1200, end_year=1300)
        self.assertIn(p, filter.qs)
        self.assertEqual(len(filter.qs), 3)
        # We get all project if it's a wrong filter

    def test_filter_year_with_string(self):
        filter = ProjectFilterSet(data={'in_year': 'toto'})
        p = ProjectFactory.create(begin_year=1200, end_year=1300)
        self.assertIn(p, filter.qs)
        self.assertEqual(len(filter.qs), 3)
        # We get all project if it's a wrong filter
