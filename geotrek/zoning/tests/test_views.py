import json

from django.test import TestCase
from django.urls import reverse
from mapentity.tests.factories import UserFactory
from rest_framework.test import APITestCase

from geotrek.zoning.templatetags.zoning_tags import (
    all_restricted_areas,
    restricted_areas_by_type,
)
from geotrek.zoning.tests.factories import (
    CityFactory,
    DistrictFactory,
    RestrictedAreaFactory,
    RestrictedAreaTypeFactory,
)


class AutocompleteTestMixin:
    factory_class = None

    def test_autocomplete_bbox_is_limit_by_10(self):
        self.factory_class.create_batch(15, name="Cahors")
        url = reverse(f"zoning:{self.layer}-autocomplete-bbox")
        response = self.client.get(url, data={"q": "Cahors"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 10)

    def test_autocomplete_bbox_has_default_values(self):
        self.factory_class.create_batch(15)
        url = reverse(f"zoning:{self.layer}-autocomplete-bbox")
        response = self.client.get(url, data={"q": ""})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 10)

    def test_autocomplete_by_id_exists(self):
        instance = self.factory_class()
        url = reverse(f"zoning:{self.layer}-autocomplete")
        response = self.client.get(url, data={"id": instance.pk})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(response.json()["id"], instance.pk)

    def test_autocomplete_by_id_not_exists(self):
        url = reverse(f"zoning:{self.layer}-autocomplete")
        response = self.client.get(url, data={"id": "999999"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertDictEqual(response.json(), {})

    def test_autocomplete_by_filtering(self):
        self.factory_class(name="Cahors")
        self.factory_class(name="Toulouse")
        url = reverse(f"zoning:{self.layer}-autocomplete")
        response = self.client.get(url, data={"q": "Cah"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 1)


class LandLayersViewsTest:
    layer = ""
    factory_class = None

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_views_status(self):
        url = reverse(f"zoning:{self.layer}-list", kwargs={"format": "geojson"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.json())


class CityViewSetTestCase(AutocompleteTestMixin, LandLayersViewsTest, APITestCase):
    layer = "city"
    factory_class = CityFactory


class DistrictViewSetTestCase(AutocompleteTestMixin, LandLayersViewsTest, APITestCase):
    layer = "district"
    factory_class = DistrictFactory


class RestrictedAreaViewTest(AutocompleteTestMixin, LandLayersViewsTest, APITestCase):
    layer = "restrictedarea"
    factory_class = RestrictedAreaFactory

    def test_view_by_type_status_is_404_when_unknown(self):
        url = reverse(
            f"zoning:{self.layer}-by-type-list",
            kwargs={"type_pk": 1023, "format": "geojson"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_view_by_type_status_is_200_when_known(self):
        t = RestrictedAreaTypeFactory()
        url = reverse(
            f"zoning:{self.layer}-by-type-list",
            kwargs={"type_pk": t.pk, "format": "geojson"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.json())

    # Restricted area do not have autocomplete bbox filter
    def test_autocomplete_bbox_is_limit_by_10(self):
        pass

    # Restricted area do not have autocomplete bbox filter
    def test_autocomplete_bbox_has_default_values(self):
        pass


class RestrictedAreasSerializationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.type_1 = RestrictedAreaTypeFactory(name="ABC")
        cls.type_2 = RestrictedAreaTypeFactory(name="AAC")
        cls.type_3 = RestrictedAreaTypeFactory(name="ABB")
        cls.type_4 = RestrictedAreaTypeFactory(name="AAA")
        cls.area_1 = RestrictedAreaFactory(area_type=cls.type_1, name="aaa")
        cls.area_2 = RestrictedAreaFactory(area_type=cls.type_1, name="aab")
        cls.area_3 = RestrictedAreaFactory(area_type=cls.type_2, name="aaa")
        cls.area_4 = RestrictedAreaFactory(area_type=cls.type_2, name="aab")
        cls.area_5 = RestrictedAreaFactory(area_type=cls.type_3, name="aab")
        cls.area_6 = RestrictedAreaFactory(area_type=cls.type_3, name="aaa")
        cls.area_7 = RestrictedAreaFactory(area_type=cls.type_4, name="aba")
        cls.area_8 = RestrictedAreaFactory(area_type=cls.type_4, name="aca")
        cls.area_9 = RestrictedAreaFactory(area_type=cls.type_4, name="aaa")

    def test_restricted_areas_by_type_serizalization(self):
        """Test restricted areas are sorted by type and ordered alphabetically within types"""
        with self.assertNumQueries(2):
            serizalized = restricted_areas_by_type()
        correct_data = json.dumps(
            {
                f"{self.type_1.pk}": {
                    "areas": [
                        {f"{self.area_1.pk}": "ABC - aaa"},
                        {f"{self.area_2.pk}": "ABC - aab"},
                    ]
                },
                f"{self.type_2.pk}": {
                    "areas": [
                        {f"{self.area_3.pk}": "AAC - aaa"},
                        {f"{self.area_4.pk}": "AAC - aab"},
                    ]
                },
                f"{self.type_3.pk}": {
                    "areas": [
                        {f"{self.area_6.pk}": "ABB - aaa"},
                        {f"{self.area_5.pk}": "ABB - aab"},
                    ]
                },
                f"{self.type_4.pk}": {
                    "areas": [
                        {f"{self.area_9.pk}": "AAA - aaa"},
                        {f"{self.area_7.pk}": "AAA - aba"},
                        {f"{self.area_8.pk}": "AAA - aca"},
                    ]
                },
            }
        )
        self.assertJSONEqual(serizalized, correct_data)

    def test_all_restricted_areas_serizalization(self):
        """Test restricted areas are ordered alphabetically by type name then by area name"""
        serizalized = all_restricted_areas()
        correct_data = json.dumps(
            [
                {f"{self.area_9.pk}": "AAA - aaa"},
                {f"{self.area_7.pk}": "AAA - aba"},
                {f"{self.area_8.pk}": "AAA - aca"},
                {f"{self.area_3.pk}": "AAC - aaa"},
                {f"{self.area_4.pk}": "AAC - aab"},
                {f"{self.area_6.pk}": "ABB - aaa"},
                {f"{self.area_5.pk}": "ABB - aab"},
                {f"{self.area_1.pk}": "ABC - aaa"},
                {f"{self.area_2.pk}": "ABC - aab"},
            ]
        )
        self.assertJSONEqual(serizalized, correct_data)
