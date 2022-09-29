
from django.test import TestCase

from geotrek.authent.tests.factories import UserFactory
from geotrek.tourism.forms import TouristicEventForm


class PathFormTest(TestCase):
    def test_begin_end_date(self):
        user = UserFactory()
        form1 = TouristicEventForm(
            user=user,
            data={
                'geom': '{"type": "Point", "coordinates":[0, 0]}',
                'name_en': 'test',
                'begin_date': '2022-01-20',
                'end_date': '2022-01-10',
            }
        )
        self.assertFalse(form1.is_valid())
        self.assertIn("Start date is after end date", str(form1.errors))
