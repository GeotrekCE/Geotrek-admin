from django.core.exceptions import ValidationError
from django.test import TestCase

from geotrek.authent.factories import UserFactory
from ..factories import TrekFactory
from ..models import OrderedTrekChild
from ..forms import TrekForm


class TrekItinerancyTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trek1 = TrekFactory(name="1")
        self.trek2 = TrekFactory(name="2")
        self.trek3 = TrekFactory(name="3")

    def test_two_children(self):
        OrderedTrekChild(child=self.trek1, parent=self.trek2, order=0).save()
        form = TrekForm(instance=self.trek2, user=self.user)
        form.cleaned_data = {'children_trek': [self.trek3]}
        form.clean_children_trek()

    def test_parent_as_child(self):
        OrderedTrekChild(child=self.trek1, parent=self.trek2, order=0).save()
        form = TrekForm(instance=self.trek3, user=self.user)
        form.cleaned_data = {'children_trek': [self.trek2]}
        with self.assertRaises(ValidationError) as cm:
            form.clean_children_trek()
        self.assertEquals(cm.exception.message, u'Cannot use parent trek 2 as a child trek.')

    def test_child_with_itself_child(self):
        OrderedTrekChild(child=self.trek1, parent=self.trek2, order=0).save()
        form = TrekForm(instance=self.trek1, user=self.user)
        form.cleaned_data = {'children_trek': [self.trek3]}
        with self.assertRaises(ValidationError) as cm:
            form.clean_children_trek()
        self.assertEquals(cm.exception.message, u'Cannot add children because this trek is itself a child.')
