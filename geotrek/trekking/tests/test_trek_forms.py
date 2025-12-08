import json

from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from geotrek.authent.tests.factories import UserFactory
from geotrek.core.tests.factories import PathFactory

from ..forms import TrekForm
from ..models import OrderedTrekChild
from .factories import RatingFactory, TrekFactory


class TrekRatingFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.path = PathFactory.create()
        cls.rating = RatingFactory()
        cls.trek = TrekFactory(practice=cls.rating.scale.practice)

    def test_ratings_save(self):
        data = {
            "name_en": "Trek",
            "practice": str(self.rating.scale.practice.pk),
            f"rating_scale_{self.rating.scale.pk}": str(self.rating.pk),
        }

        if settings.TREKKING_TOPOLOGY_ENABLED:
            data["topology"] = json.dumps({"paths": [self.path.pk]})
        else:
            data["geom"] = "SRID=4326;LINESTRING (0.0 0.0, 1.0 1.0)"

        form = TrekForm(user=self.user, instance=self.trek, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertListEqual(
            list(self.trek.ratings.all().values_list("pk", flat=True)), [self.rating.pk]
        )

    def test_no_rating_save(self):
        data = {
            "name_en": "Trek",
            "practice": str(self.rating.scale.practice.pk),
        }

        if settings.TREKKING_TOPOLOGY_ENABLED:
            data["topology"] = json.dumps({"paths": [self.path.pk]})
        else:
            data["geom"] = "SRID=4326;LINESTRING (0.0 0.0, 1.0 1.0)"

        form = TrekForm(user=self.user, instance=self.trek, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertQuerySetEqual(self.trek.ratings.all(), [])

    def test_ratings_clean(self):
        other_rating = RatingFactory()
        data = {
            "name_en": "Trek",
            "practice": str(self.rating.scale.practice.pk),
            f"rating_scale_{other_rating.scale.pk}": str(other_rating.pk),
        }

        if settings.TREKKING_TOPOLOGY_ENABLED:
            data["topology"] = json.dumps({"paths": [self.path.pk]})

        else:
            data["geom"] = "SRID=4326;LINESTRING (0.0 0.0, 1.0 1.0)"

        form = TrekForm(user=self.user, instance=self.trek, data=data)

        self.assertFalse(form.is_valid())
        with self.assertRaisesRegex(
            ValidationError,
            "One of the rating scale used is not part of the practice chosen",
        ):
            form.clean()


@override_settings(
    COMPLETENESS_FIELDS={
        "trek": ["practice", "departure", "duration", "description_teaser"]
    }
)
class TrekCompletenessTest(TestCase):
    """Test completeness fields on error if empty, according to COMPLETENESS_LEVEL setting"""

    @classmethod
    def setUpTestData(cls):
        call_command("update_geotrek_permissions", verbosity=0)
        cls.user = UserFactory.create()
        cls.user.user_permissions.add(Permission.objects.get(codename="publish_trek"))
        path = PathFactory.create()
        cls.data = {
            "name_en": "My trek",
            "name_fr": "Ma rando",
        }

        if settings.TREKKING_TOPOLOGY_ENABLED:
            cls.data["topology"] = json.dumps({"paths": [path.pk]})
        else:
            cls.data["geom"] = "SRID=4326;LINESTRING (0.0 0.0, 1.0 1.0)"

    def test_completeness_warning(self):
        """Test form is valid if completeness level is only warning"""
        data = self.data
        data["published_en"] = True

        form = TrekForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())

    @override_settings(COMPLETENESS_LEVEL="error_on_publication")
    def test_completeness_error_on_publish_not_published(self):
        """Test form is valid if completeness level is error on publication but published in no language"""
        data = self.data
        data["published_en"] = False

        form = TrekForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())

    @override_settings(COMPLETENESS_LEVEL="error_on_publication")
    def test_completeness_error_on_publish_en(self):
        """Test completeness fields on error if empty"""
        data = self.data
        data["published_en"] = True

        form = TrekForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        with self.assertRaisesRegex(
            ValidationError,
            "Fields are missing to publish or review object: "
            "practice, departure_en, duration, description_teaser_en",
        ):
            form.clean()

    @override_settings(COMPLETENESS_LEVEL="error_on_publication")
    def test_completeness_error_on_publish_fr(self):
        """Test completeness fields on error if empty"""
        data = self.data
        data["published_en"] = False
        data["published_fr"] = True

        form = TrekForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        with self.assertRaisesRegex(
            ValidationError,
            "Fields are missing to publish or review object: "
            "practice, departure_fr, duration, description_teaser_fr",
        ):
            form.clean()

    @override_settings(PUBLISHED_BY_LANG=False)
    @override_settings(COMPLETENESS_LEVEL="error_on_publication")
    def test_completeness_error_on_publish_nolang(self):
        """Test completeness fields on error if empty (when PUBLISHED_BY_LANG=False)"""
        data = self.data
        data["published_en"] = True
        data["published_fr"] = False

        form = TrekForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        with self.assertRaisesRegex(
            ValidationError,
            "Fields are missing to publish or review object: "
            "practice, departure_en, departure_es, departure_fr, departure_it, duration, "
            "description_teaser_en, description_teaser_es, "
            "description_teaser_fr, description_teaser_it",
        ):
            form.clean()

    @override_settings(COMPLETENESS_LEVEL="error_on_review")
    def test_completeness_error_on_review(self):
        """Test completeness fields on error if empty and is review, with 'error_on_review'"""
        data = self.data
        data["published_en"] = False
        data["review"] = True
        form = TrekForm(user=self.user, data=data)

        self.assertFalse(form.is_valid())
        with self.assertRaisesRegex(
            ValidationError,
            "Fields are missing to publish or review object: "
            "practice, departure_en, duration, description_teaser_en",
        ):
            form.clean()

        # Exception should raise also if object is to be published
        data["published_en"] = False
        data["published_fr"] = True
        data["review"] = False
        form = TrekForm(user=self.user, data=data)

        self.assertFalse(form.is_valid())
        with self.assertRaisesRegex(
            ValidationError,
            "Fields are missing to publish or review object: "
            "practice, departure_fr, duration, description_teaser_fr",
        ):
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
            "children_trek": [self.trek3],
            "hidden_ordered_children": str(self.trek3.pk),
        }
        form.clean_children_trek()

    def test_parent_as_child(self):
        OrderedTrekChild(child=self.trek1, parent=self.trek2, order=0).save()
        form = TrekForm(instance=self.trek3, user=self.user)
        form.cleaned_data = {
            "children_trek": [self.trek2],
            "hidden_ordered_children": str(self.trek2.pk),
        }
        with self.assertRaisesRegex(
            ValidationError, "Cannot use parent trek 2 as a child trek."
        ):
            form.clean_children_trek()

    def test_child_with_itself_child(self):
        OrderedTrekChild(child=self.trek1, parent=self.trek2, order=0).save()
        form = TrekForm(instance=self.trek1, user=self.user)
        form.cleaned_data = {
            "children_trek": [self.trek3],
            "hidden_ordered_children": str(self.trek3.pk),
        }
        with self.assertRaisesRegex(
            ValidationError, "Cannot add children because this trek is itself a child."
        ):
            form.clean_children_trek()
