import json

from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from mapentity.tests import MapEntityTest, SuperUserFactory
from mapentity.tests.factories import UserFactory
from rest_framework.test import APITestCase

from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import StructureFactory, UserProfileFactory
from geotrek.zoning.choices import Practicability
from geotrek.zoning.models import VigilanceArea
from geotrek.zoning.serializers import VigilanceAreaSerializer
from geotrek.zoning.tests.factories import (
    CityFactory,
    DistrictFactory,
    RestrictedAreaFactory,
    RestrictedAreaTypeFactory,
    VigilanceAreaFactory,
    VigilanceAreaTypeFactory,
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

    def test_autocomplete_bbox_custom_page_size(self):
        self.factory_class.create_batch(20, name="Test")
        url = reverse(f"zoning:{self.layer}-autocomplete-bbox")
        response = self.client.get(url, data={"q": "Test", "page_size": "5"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertTrue(response.json()["pagination"]["more"])

    def test_autocomplete_bbox_pagination_different_pages(self):
        # Create 25 items to test pagination across multiple pages
        for i in range(25):
            self.factory_class(name=f"Item{i}")
        url = reverse(f"zoning:{self.layer}-autocomplete-bbox")

        # Test first page
        response = self.client.get(url, data={"page": "1", "page_size": "10"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 10)
        self.assertTrue(response.json()["pagination"]["more"])

        # Test second page
        response = self.client.get(url, data={"page": "2", "page_size": "10"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 10)
        self.assertTrue(response.json()["pagination"]["more"])

        # Test third page (last page with 5 items)
        response = self.client.get(url, data={"page": "3", "page_size": "10"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertFalse(response.json()["pagination"]["more"])

    def test_autocomplete_bbox_pagination_more_field_false(self):
        self.factory_class.create_batch(5, name="Test")
        url = reverse(f"zoning:{self.layer}-autocomplete-bbox")
        response = self.client.get(url, data={"q": "Test", "page_size": "10"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertFalse(response.json()["pagination"]["more"])

    def test_autocomplete_bbox_pagination_more_field_true(self):
        self.factory_class.create_batch(15, name="Test")
        url = reverse(f"zoning:{self.layer}-autocomplete-bbox")
        response = self.client.get(url, data={"q": "Test", "page_size": "10"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 10)
        self.assertTrue(response.json()["pagination"]["more"])

    def test_autocomplete_bbox_page_beyond_data(self):
        self.factory_class.create_batch(5, name="Test")
        url = reverse(f"zoning:{self.layer}-autocomplete-bbox")
        response = self.client.get(
            url, data={"q": "Test", "page": "10", "page_size": "10"}
        )
        self.assertEqual(response.status_code, 200, response.json())
        # Django's Paginator.get_page() returns the last page when page is beyond data
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertFalse(response.json()["pagination"]["more"])

    def test_autocomplete_bbox_invalid_page_parameter(self):
        self.factory_class.create_batch(5, name="Test")
        url = reverse(f"zoning:{self.layer}-autocomplete-bbox")
        # View error handling treats invalid page as page 1
        response = self.client.get(url, data={"q": "Test", "page": "invalid"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 5)

    def test_autocomplete_bbox_invalid_page_size_parameter(self):
        self.factory_class.create_batch(15, name="Test")
        url = reverse(f"zoning:{self.layer}-autocomplete-bbox")
        # View code handles invalid page_size by converting to int and defaulting to 10
        response = self.client.get(url, data={"q": "Test", "page_size": "invalid"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 10)
        self.assertTrue(response.json()["pagination"]["more"])

    def test_autocomplete_custom_page_size(self):
        self.factory_class.create_batch(20, name="Test")
        url = reverse(f"zoning:{self.layer}-autocomplete")
        response = self.client.get(url, data={"q": "Test", "page_size": "5"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertTrue(response.json()["pagination"]["more"])

    def test_autocomplete_pagination_different_pages(self):
        # Create 25 items to test pagination across multiple pages
        for i in range(25):
            self.factory_class(name=f"Item{i}")
        url = reverse(f"zoning:{self.layer}-autocomplete")

        # Test first page
        response = self.client.get(url, data={"page": "1", "page_size": "10"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 10)
        self.assertTrue(response.json()["pagination"]["more"])

        # Test second page
        response = self.client.get(url, data={"page": "2", "page_size": "10"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 10)
        self.assertTrue(response.json()["pagination"]["more"])

        # Test third page (last page with 5 items)
        response = self.client.get(url, data={"page": "3", "page_size": "10"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertFalse(response.json()["pagination"]["more"])

    def test_autocomplete_pagination_more_field_false(self):
        self.factory_class.create_batch(5, name="Test")
        url = reverse(f"zoning:{self.layer}-autocomplete")
        response = self.client.get(url, data={"q": "Test", "page_size": "10"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertFalse(response.json()["pagination"]["more"])

    def test_autocomplete_pagination_more_field_true(self):
        self.factory_class.create_batch(15, name="Test")
        url = reverse(f"zoning:{self.layer}-autocomplete")
        response = self.client.get(url, data={"q": "Test", "page_size": "10"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 10)
        self.assertTrue(response.json()["pagination"]["more"])

    def test_autocomplete_page_beyond_data(self):
        self.factory_class.create_batch(5, name="Test")
        url = reverse(f"zoning:{self.layer}-autocomplete")
        response = self.client.get(
            url, data={"q": "Test", "page": "10", "page_size": "10"}
        )
        self.assertEqual(response.status_code, 200, response.json())
        # Django's Paginator.get_page() returns the last page when page is beyond data
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertFalse(response.json()["pagination"]["more"])

    def test_autocomplete_invalid_page_parameter(self):
        self.factory_class.create_batch(5, name="Test")
        url = reverse(f"zoning:{self.layer}-autocomplete")
        # View error handling treats invalid page as page 1
        response = self.client.get(url, data={"q": "Test", "page": "invalid"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 5)

    def test_autocomplete_invalid_page_size_parameter(self):
        self.factory_class.create_batch(15, name="Test")
        url = reverse(f"zoning:{self.layer}-autocomplete")
        # View code handles invalid page_size by converting to int and defaulting to 10
        response = self.client.get(url, data={"q": "Test", "page_size": "invalid"})
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 10)
        self.assertTrue(response.json()["pagination"]["more"])

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

    def test_autocomplete_forward(self):
        type_1 = RestrictedAreaTypeFactory()
        type_1_areas = RestrictedAreaFactory.create_batch(2, area_type=type_1)
        type_2 = RestrictedAreaTypeFactory()
        RestrictedAreaFactory.create_batch(2, area_type=type_2)
        url = reverse(f"zoning:{self.layer}-autocomplete")
        response = self.client.get(
            url, data={"forward": json.dumps({"area_type": [type_1.pk]})}
        )
        self.assertEqual(response.status_code, 200, response.json())
        self.assertEqual(len(response.json()["results"]), 2)
        self.assertEqual(
            {area["id"] for area in response.json()["results"]},
            {area.pk for area in type_1_areas},
        )


class VigilanceAreaTestCase(MapEntityTest):
    model = VigilanceArea
    modelfactory = VigilanceAreaFactory
    userfactory = SuperUserFactory
    maxDiff = None

    def get_good_data(self):
        area_type = VigilanceAreaTypeFactory()
        structure = StructureFactory.create()
        return {
            "id": 1,
            "name_en": "my area",
            "practicability": Practicability.PRACTICABLE.value,
            "vigilance_area_type": area_type.pk,
            "structure": structure.pk,
            "start_date": "2026-07-06",
            "geom": "MULTIPOLYGON(((-0.3142392 -1.0870745, -0.4442674 1.9698002, 2.6553568 2.0446445, 2.6683833 -1.0177449, -0.3142392 -1.0870745)))",
        }

    extra_column_list = ["eid"]
    expected_column_list_extra = ["id", "physical_type", "eid"]
    expected_column_formatlist_extra = ["id", "physical_type", "eid"]
    expected_json_geom = {
        "coordinates": [
            [
                [
                    [-0.3142392, -1.0870745],
                    [-0.4442674, 1.9698002],
                    [2.6553568, 2.0446445],
                    [2.6683833, -1.0177449],
                    [-0.3142392, -1.0870745],
                ]
            ]
        ],
        "type": "MultiPolygon",
    }

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {"id": self.obj.pk, "name": self.obj.name, "published": False}

    def get_expected_datatables_attrs(self):
        return {
            "id": self.obj.pk,
            "name": f'<a data-pk="{self.obj.pk}" href="/vigilancearea/{self.obj.pk}/" title="{self.obj.name}">{self.obj.name}</a>',
            "period_active": '<i class="bi bi-check-circle text-success"></i>',
            "practicability": Practicability.PRACTICABLE.label,
            "vigilance_area_type": self.obj.vigilance_area_type.name,
        }

    def get_expected_popup_content(self):
        return (
            f'<div class="d-flex flex-column justify-content-center">\n'
            f'    <p class="text-center m-0 p-1"><strong>{str(self.obj)}</strong></p>\n    \n'
            f'    <a id="detail-btn" href="/vigilancearea/{self.obj.pk}/" class="btn btn-sm btn-info mt-2">Detail sheet</a>\n'
            f"</div>"
        )


class VigilanceAreaDetailViewTest(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        profile = UserProfileFactory.create(
            user__username="testuser", user__password="password"
        )
        cls.user = profile.user
        cls.user.groups.add(Group.objects.get(name="Référents communication"))
        cls.user.user_permissions.add(
            Permission.objects.get(codename="read_vigilancearea")
        )
        cls.area_same_struct = VigilanceAreaFactory(
            structure=cls.user.profile.structure
        )
        cls.other_struct = StructureFactory()
        cls.area_other_struct = VigilanceAreaFactory(structure=cls.other_struct)

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_can_edit_context_flag(self):
        url_same = reverse(
            "zoning:vigilancearea_detail", kwargs={"pk": self.area_same_struct.pk}
        )
        response_same = self.client.get(url_same)
        self.assertEqual(response_same.status_code, 200)
        self.assertTrue(response_same.context["can_edit"])

        url_other = reverse(
            "zoning:vigilancearea_detail", kwargs={"pk": self.area_other_struct.pk}
        )
        response_other = self.client.get(url_other)
        self.assertEqual(response_other.status_code, 200)
        self.assertFalse(response_other.context["can_edit"])


class VigilanceAreaSerializerTest(TestCase):
    def test_serializer_output(self):
        area = VigilanceAreaFactory(practicability=Practicability.PRACTICABLE)
        qs = VigilanceArea.objects.all()
        serializer = VigilanceAreaSerializer(qs.get(pk=area.pk))
        data = serializer.data
        self.assertIn(area.name, data["name"])
        self.assertEqual(data["practicability"], Practicability.PRACTICABLE.label)
        self.assertIn("period_active", data)
