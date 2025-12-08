from django.test import TestCase

from geotrek.maintenance.models import Intervention
from geotrek.maintenance.tests.factories import InterventionFactory


class InterventionManagerTest(TestCase):
    def test_intervention_with_not_end_date(self):
        InterventionFactory(name="test1", begin_date="2020-06-03")
        InterventionFactory(name="test2", begin_date="2022-06-03")
        self.assertEqual(
            Intervention.objects.year_choices(), [(2022, 2022), (2020, 2020)]
        )

    def test_intervention_with_end_date(self):
        InterventionFactory(
            name="test1", begin_date="2018-06-03", end_date="2020-06-03"
        )
        InterventionFactory(
            name="test2", begin_date="2022-06-03", end_date="2024-06-03"
        )
        self.assertEqual(
            Intervention.objects.year_choices(),
            [
                (2024, 2024),
                (2023, 2023),
                (2022, 2022),
                (2020, 2020),
                (2019, 2019),
                (2018, 2018),
            ],
        )

    def test_intervention_with_one_have_end_date(self):
        InterventionFactory(name="test1", begin_date="2020-06-03")
        InterventionFactory(
            name="test2", begin_date="2022-06-03", end_date="2024-06-03"
        )
        self.assertEqual(
            Intervention.objects.year_choices(),
            [(2024, 2024), (2023, 2023), (2022, 2022), (2020, 2020)],
        )

    def test_intervention_return_distinct_year(self):
        InterventionFactory(name="test1", begin_date="2020-06-03")
        InterventionFactory(
            name="test2", begin_date="2018-06-03", end_date="2024-06-03"
        )
        self.assertEqual(
            Intervention.objects.year_choices(),
            [
                (2024, 2024),
                (2023, 2023),
                (2022, 2022),
                (2021, 2021),
                (2020, 2020),
                (2019, 2019),
                (2018, 2018),
            ],
        )
