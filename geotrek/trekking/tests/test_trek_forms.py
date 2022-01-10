from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase

from geotrek.authent.tests.factories import UserFactory
from geotrek.core.tests.factories import PathFactory
from .factories import TrekFactory, RatingFactory
from ..models import OrderedTrekChild
from ..forms import TrekForm


class TrekFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.path = PathFactory.create()
        cls.rating = RatingFactory()
        cls.trek = TrekFactory(practice=cls.rating.scale.practice)

    def test_ratings_save(self):
        data = {
            'name_en': 'Trek',
            'practice': str(self.rating.scale.practice.pk),
            'rating_scale_{}'.format(self.rating.scale.pk): [str(self.rating.pk)],
            'topology': '{"paths": [%s]}' % self.path.pk
        }

        if settings.TREKKING_TOPOLOGY_ENABLED:
            data['topology'] = '{"paths": [%s]}' % self.path.pk
        else:
            data['geom'] = 'SRID=4326;LINESTRING (0.0 0.0, 1.0 1.0)'

        form = TrekForm(user=self.user, instance=self.trek, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertQuerysetEqual(self.trek.ratings.all(), ['<Rating: Rating>'])

    def test_no_rating_save(self):
        data = {
            'name_en': 'Trek',
            'practice': str(self.rating.scale.practice.pk),
            'topology': '{"paths": [%s]}' % self.path.pk
        }

        if settings.TREKKING_TOPOLOGY_ENABLED:
            data['topology'] = '{"paths": [%s]}' % self.path.pk
        else:
            data['geom'] = 'SRID=4326;LINESTRING (0.0 0.0, 1.0 1.0)'

        form = TrekForm(user=self.user, instance=self.trek, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertQuerysetEqual(self.trek.ratings.all(), [])


class TrekItinerancyTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.trek1 = TrekFactory(name="1")
        self.trek2 = TrekFactory(name="2")
        self.trek3 = TrekFactory(name="3")

    def test_two_children(self):
        OrderedTrekChild(child=self.trek1, parent=self.trek2, order=0).save()
        form = TrekForm(instance=self.trek2, user=self.user)
        form.cleaned_data = {
            'children_trek': [self.trek3],
            'hidden_ordered_children': str(self.trek3.pk),
        }
        form.clean_children_trek()

    def test_parent_as_child(self):
        OrderedTrekChild(child=self.trek1, parent=self.trek2, order=0).save()
        form = TrekForm(instance=self.trek3, user=self.user)
        form.cleaned_data = {
            'children_trek': [self.trek2],
            'hidden_ordered_children': str(self.trek2.pk),
        }
        with self.assertRaisesRegex(ValidationError, 'Cannot use parent trek 2 as a child trek.'):
            form.clean_children_trek()

    def test_child_with_itself_child(self):
        OrderedTrekChild(child=self.trek1, parent=self.trek2, order=0).save()
        form = TrekForm(instance=self.trek1, user=self.user)
        form.cleaned_data = {
            'children_trek': [self.trek3],
            'hidden_ordered_children': str(self.trek3.pk),
        }
        with self.assertRaisesRegex(ValidationError, 'Cannot add children because this trek is itself a child.'):
            form.clean_children_trek()
