from django.forms import HiddenInput
from django.test import TestCase, override_settings

from geotrek.authent.tests.factories import UserFactory
from geotrek.signage.tests.factories import SignageFactory, BladeFactory, LineFactory
from geotrek.signage.forms import BladeForm, LineFormset
from geotrek.signage.models import Line


class BladeFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.signage = SignageFactory()

    def test_first_int(self):
        form = BladeForm(user=self.user, initial={'signage': self.signage})
        self.assertEqual(form.fields['number'].initial, "1")

    def test_second_int(self):
        BladeFactory(signage=self.signage, number="1")
        form = BladeForm(user=self.user, initial={'signage': self.signage})
        self.assertEqual(form.fields['number'].initial, "2")

    @override_settings(BLADE_CODE_TYPE=str)
    def test_first_str(self):
        form = BladeForm(user=self.user, initial={'signage': self.signage})
        self.assertEqual(form.fields['number'].initial, "A")

    @override_settings(BLADE_CODE_TYPE=str)
    def test_second_str(self):
        BladeFactory(signage=self.signage, number="A")
        form = BladeForm(user=self.user, initial={'signage': self.signage})
        self.assertEqual(form.fields['number'].initial, "B")

    @override_settings(BLADE_CODE_TYPE=str)
    def test_last_str(self):
        BladeFactory(signage=self.signage, number="Z")
        form = BladeForm(user=self.user, initial={'signage': self.signage})
        self.assertEqual(form.fields['number'].initial, None)

    def test_lines_formset(self):
        blade = BladeFactory.create()
        blade.lines.all().delete()
        line_1 = LineFactory.create(blade=blade, number=4)
        line_2 = LineFactory.create(blade=blade, number=5)
        data = {
            'lines-TOTAL_FORMS': '2',
            'lines-INITIAL_FORMS': '2',
            'lines-MIN_NUM_FORMS': '0',
            'lines-MAX_NUM_FORMS': '0',
            'lines-0-id': str(line_1.pk),
            'lines-0-number': 2,
            'lines-0-text': 'test',
            'lines-0-distance': 0.2,
            'lines-0-pictogram-name': 'pictogram_foo',
            'lines-0-time': 5,
            'lines-1-id': str(line_2.pk),
            'lines-1-number': 5,
            'lines-1-text': 'test',
            'lines-1-distance': 0.2,
            'lines-1-pictogram-name': 'pictogram_foo',
            'lines-1-time': 5
        }
        formset = LineFormset(data, instance=blade)
        formset.save()
        self.assertTrue(formset.is_valid())
        self.assertEqual(Line.objects.count(), 2)
        data['lines-0-DELETE'] = 'on'
        data['lines-1-DELETE'] = 'on'
        formset = LineFormset(data, instance=blade)
        formset.save()
        self.assertTrue(formset.is_valid())
        self.assertEqual(Line.objects.count(), 0)

    def test_direction_field_visibility(self):
        blade_form = BladeForm(user=self.user, initial={'signage': self.signage})
        self.assertIn('direction', blade_form.fields)
        line_form = LineFormset().forms[0]
        self.assertNotIn('direction', line_form.fields)

    @override_settings(DIRECTION_ON_LINES_ENABLED=True)
    def test_direction_field_visibility_when_direction_on_lines_enabled(self):
        blade_form = BladeForm(user=self.user, initial={'signage': self.signage})
        self.assertNotIn('direction', blade_form.fields)
        line_form = LineFormset().forms[0]
        self.assertIn('direction', line_form.fields)

    @override_settings(HIDDEN_FORM_FIELDS={'blade': ['direction']})
    def test_direction_field_cannot_be_hidden(self):
        blade_form = BladeForm(user=self.user, initial={'signage': self.signage})
        self.assertIn('direction', blade_form.fields)
        self.assertTrue(not isinstance(blade_form.fields['direction'].widget, HiddenInput))
