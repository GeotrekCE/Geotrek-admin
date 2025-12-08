from django.db.models import BooleanField
from django.test import SimpleTestCase

from geotrek.api.v2 import utils as api_utils


class FakeNotTranslatedPublishableModel:
    def __init__(self, published):
        self.published = published
        self._meta = self

    def get_fields(self):
        return [BooleanField(name="published")]


class FakeTranslatedPublishableModel:
    def __init__(self, **kwargs):
        # partial init to comply with translation languages from the test settings
        assert "published_es" not in kwargs
        kwargs["published_es"] = False
        assert "published_it" not in kwargs
        kwargs["published_it"] = False

        self._meta = self
        self.fields = []
        for k, v in kwargs.items():
            setattr(self, k, v)
            self.fields.append(BooleanField(name=k))

    def get_fields(self):
        return self.fields


class IsPublishedTestCase(SimpleTestCase):
    def test_not_published_with_not_translated_instance(self):
        instance = FakeNotTranslatedPublishableModel(published=False)
        result = api_utils.is_published(instance)
        self.assertEqual(result, False)

    def test_published_with_not_translated_instance(self):
        instance = FakeNotTranslatedPublishableModel(published=True)
        result = api_utils.is_published(instance)
        self.assertEqual(result, True)

    def test_published(self):
        params_list = [
            {"published_fr": True, "published_en": True, "expected": True},
            {"published_fr": True, "published_en": False, "expected": True},
            {"published_fr": False, "published_en": True, "expected": True},
            {"published_fr": False, "published_en": False, "expected": False},
            {
                "published_fr": True,
                "published_en": False,
                "language": "fr",
                "expected": True,
            },
            {
                "published_fr": False,
                "published_en": True,
                "language": "fr",
                "expected": False,
            },
            {
                "published_fr": True,
                "published_en": False,
                "language": "all",
                "expected": True,
            },
        ]
        for params in params_list:
            with self.subTest(**params):
                instance = FakeTranslatedPublishableModel(
                    published_fr=params["published_fr"],
                    published_en=params["published_en"],
                )
                result = api_utils.is_published(
                    instance, language=params.get("language")
                )
                self.assertEqual(result, params["expected"])
