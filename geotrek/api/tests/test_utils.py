from unittest import mock

from django.contrib.gis.geos import Point
from django.db.models import BooleanField
from django.test import SimpleTestCase

from geotrek.api.v2 import utils as api_utils
from geotrek.api.v2.renderers import RawGeoJSONRenderer, RawJSON, RawJSONRenderer
from geotrek.api.v2.serializers import (
    BaseGeoJSONSerializer,
    RawGeoJSONField,
    TouristicEventSerializer,
)


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

    def test_build_url_without_server_name_in_context(self):
        class DummySerializer:
            context = {}

        with self.assertRaisesMessage(
            Exception, "Bad context. No server variable found in the request !"
        ):
            api_utils.build_url(DummySerializer(), "/media/test.png")

    def test_touristic_event_serializer_get_type_none(self):
        self.assertIsNone(
            TouristicEventSerializer().get_type(mock.MagicMock(type=None))
        )


class RawJSONTestCase(SimpleTestCase):
    def test_raw_json_accessors(self):
        raw = RawJSON('{"type":"Point","coordinates":[1.2,3.4]}')
        self.assertEqual(raw.get("type"), "Point")
        self.assertEqual(raw["coordinates"], [1.2, 3.4])
        self.assertIsNone(raw.get("missing"))

    def test_raw_json_renderer_none_and_indent(self):
        renderer = RawJSONRenderer()
        self.assertEqual(renderer.render(None), b"")
        rendered = renderer.render(
            {"geometry": RawJSON('{"type":"Point","coordinates":[1,2]}'), "id": 1},
            accepted_media_type="application/json; indent=2",
        )
        self.assertIn(
            b'{\n  "geometry": {"type":"Point","coordinates":[1,2]}', rendered
        )

    def test_raw_geojson_renderer(self):
        renderer = RawGeoJSONRenderer()
        self.assertEqual(renderer.format, "geojson")
        self.assertEqual(renderer.media_type, "application/geo+json")
        rendered = renderer.render(
            {
                "type": "Feature",
                "geometry": RawJSON('{"type":"Point","coordinates":[1,2]}'),
            }
        )
        self.assertIn(b'"geometry":{"type":"Point","coordinates":[1,2]}', rendered)

    def test_raw_geojson_field_none_str_and_geos_fallback(self):
        field = RawGeoJSONField()
        self.assertIsNone(field.to_representation(None))
        raw = field.to_representation('{"type":"Point","coordinates":[1,2]}')
        self.assertIsInstance(raw, RawJSON)
        point = Point(1.123456789, 2.987654321, srid=4326)
        rep = field.to_representation(point)
        self.assertEqual(rep["type"], "Point")
        self.assertEqual(rep["coordinates"], (1.1234568, 2.9876543))

    def test_base_geojson_serializer_geos_fallback_bbox(self):
        from geotrek.zoning.models import City

        class DummyGeoSerializer(BaseGeoJSONSerializer):
            geometry = RawGeoJSONField(source="geom_geojson")

            class Meta(BaseGeoJSONSerializer.Meta):
                model = City
                id_field = False
                fields = ("geometry",)

            def get_properties(self, instance, fields):
                return {}

        point = Point(1.123456789, 2.987654321, srid=4326)
        instance = mock.MagicMock(spec=["geom_geojson"], geom_geojson=point)
        feature = DummyGeoSerializer().to_representation(instance)
        self.assertEqual(feature["bbox"], [1.1234568, 2.9876543, 1.1234568, 2.9876543])
