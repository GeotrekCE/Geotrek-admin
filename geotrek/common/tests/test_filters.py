from django.test import TestCase

from geotrek.maintenance.filters import ProjectFilterSet
from geotrek.maintenance.tests.factories import ProjectFactory


class ProjectYearsFilterTest(TestCase):
    def test_filter_year_with_string(self):
        ProjectFactory.create(begin_year=1500, end_year=2000)
        ProjectFactory.create(begin_year=1700, end_year=1800)
        self.filter = ProjectFilterSet()
        self.widget = self.filter.filters["year"].field.widget
        filter = ProjectFilterSet(data={"year": "toto"})
        p = ProjectFactory.create(begin_year=1200, end_year=1300)
        self.assertIn(p, filter.qs)
        self.assertEqual(len(filter.qs), 3)
        # We get all project if it's a wrong filter
