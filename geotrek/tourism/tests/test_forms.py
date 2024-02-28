
from django.forms.widgets import Select
from django.test import TestCase
from django.contrib.auth.models import Permission

from mapentity.widgets import SelectMultipleWithPop

from geotrek.authent.tests.factories import UserFactory
from geotrek.tourism.forms import TouristicEventForm


class PathFormTest(TestCase):
    def test_begin_end_time(self):
        data = {
            'geom': '{"type": "Point", "coordinates":[0, 0]}',
            'name_en': 'test',
            'begin_date': '2022-01-20',
            'end_date': '2022-01-20'
        }
        user = UserFactory()

        # No start no end time
        form = TouristicEventForm(
            user=user,
            data=data
        )
        self.assertTrue(form.is_valid())

        # No start, end time
        form = TouristicEventForm(
            user=user,
            data={
                **data,
                **{'end_time': '10:30'}
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Start time is unset", str(form.errors))

        # No end date and start time > end time
        form = TouristicEventForm(
            user=user,
            data={
                **data,
                **{
                    'end_date': None,
                    'start_time': '11:30',
                    'end_time': '10:30'
                }
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Start time is after end time", str(form.errors))

        # Begin and end date and start time > end time
        form = TouristicEventForm(
            user=user,
            data={
                **data,
                **{
                    'start_time': '11:30',
                    'end_time': '10:30'
                }
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Start time is after end time", str(form.errors))

        # No end time
        form = TouristicEventForm(
            user=user,
            data={
                **data,
                **{'start_time': '10:30'}
            }
        )
        self.assertTrue(form.is_valid())

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

    def test_organizers_widget_select(self):
        # if user has 'add_touristiceventorganizer' permission the widget must be a SelectMultipleWithPop
        # otherwith a Select
        form = TouristicEventForm(
            user=UserFactory(),
            data={}
        )
        assert type(form.fields['organizer'].widget) is Select

    def test_organizers_widget_select_multiple_with_pop(self):
        # if user has 'add_touristiceventorganizer' permission the widget must be a SelectMultipleWithPop
        # otherwith a Select
        user = UserFactory()
        user.user_permissions.add(Permission.objects.get(codename='add_touristiceventorganizer'))
        form = TouristicEventForm(
            user=user,
            data={}
        )
        assert type(form.fields['organizer'].widget) is SelectMultipleWithPop
