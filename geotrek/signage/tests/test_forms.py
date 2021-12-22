from django.test import TestCase, override_settings

from geotrek.authent.tests.factories import UserFactory
from geotrek.signage.tests.factories import SignageFactory, BladeFactory, LineFactory
from geotrek.signage.forms import BladeForm, LineFormset
from geotrek.signage.models import Line


class BladeFormTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.signage = SignageFactory()

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
