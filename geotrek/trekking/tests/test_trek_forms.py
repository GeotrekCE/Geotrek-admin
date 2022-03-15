import json
from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.utils import override_settings

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
            'rating_scale_{}'.format(self.rating.scale.pk): str(self.rating.pk),
        }

        if settings.TREKKING_TOPOLOGY_ENABLED:
            data['topology'] = json.dumps({"paths": [self.path.pk]})
        else:
            data['geom'] = 'SRID=4326;LINESTRING (0.0 0.0, 1.0 1.0)'

        form = TrekForm(user=self.user, instance=self.trek, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertQuerysetEqual(self.trek.ratings.all(), ['<Rating: RatingScale : Rating>'])

    def test_no_rating_save(self):
        data = {
            'name_en': 'Trek',
            'practice': str(self.rating.scale.practice.pk),
        }

        if settings.TREKKING_TOPOLOGY_ENABLED:
            data['topology'] = json.dumps({"paths": [self.path.pk]})
        else:
            data['geom'] = 'SRID=4326;LINESTRING (0.0 0.0, 1.0 1.0)'

        form = TrekForm(user=self.user, instance=self.trek, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertQuerysetEqual(self.trek.ratings.all(), [])

    def test_ratings_clean(self):
        other_rating = RatingFactory()
        data = {
            'name_en': 'Trek',
            'practice': str(self.rating.scale.practice.pk),
            f'rating_scale_{other_rating.scale.pk}': str(other_rating.pk),
        }

        if settings.TREKKING_TOPOLOGY_ENABLED:
            data['topology'] = json.dumps({"paths": [self.path.pk]})

        else:
            data['geom'] = 'SRID=4326;LINESTRING (0.0 0.0, 1.0 1.0)'

        form = TrekForm(user=self.user, instance=self.trek, data=data)

        self.assertFalse(form.is_valid())
        with self.assertRaisesRegex(ValidationError, 'One of the rating scale used is not part of the practice chosen'):
            form.clean()


class TreckCompletenessTest(TestCase):
    """Test completeness fields on error if empty"""
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.path = PathFactory.create()
        cls.trek = TrekFactory()

    def test_completeness_error(self):
        """Test completeness fields on error if empty"""
        data = {
            'name_en': 'Trek',
            'published_en': True,
        }

        if settings.TREKKING_TOPOLOGY_ENABLED:
            data['topology'] = json.dumps({"paths": [self.path.pk]})

        else:
            data['geom'] = 'SRID=4326;LINESTRING (0.0 0.0, 1.0 1.0)'

        with override_settings(COMPLETENESS_MODE='error_on_publication'):
            form = TrekForm(user=self.user, instance=self.trek, data=data)
            self.assertFalse(form.is_valid())
            with self.assertRaises(ValidationError, 'One of the rating scale used is not part of the practice chosen'):
                form.clean()


class TrekItinerancyTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.trek1 = TrekFactory(name="1")
        cls.trek2 = TrekFactory(name="2")
        cls.trek3 = TrekFactory(name="3")

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
