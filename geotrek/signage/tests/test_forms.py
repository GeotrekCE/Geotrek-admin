from django.test import TestCase, override_settings

from geotrek.authent.tests.factories import UserFactory
from geotrek.signage.tests.factories import SignageFactory, BladeFactory
from geotrek.signage.forms import BladeForm


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
