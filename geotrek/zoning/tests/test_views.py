import json

from django.test import TestCase
from django.urls import reverse

from geotrek.zoning.tests.factories import RestrictedAreaFactory, RestrictedAreaTypeFactory
from geotrek.zoning.templatetags.zoning_tags import all_restricted_areas, restricted_areas_by_type


class LandLayersViewsTest(TestCase):

    def test_views_status(self):
        for layer in ['city', 'restrictedarea', 'district']:
            url = reverse('zoning:%s_layer' % layer)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)


class RestrictedAreaViewsTest(TestCase):

    def test_views_status_is_404_when_type_unknown(self):
        url = reverse('zoning:restrictedarea_type_layer', kwargs={'type_pk': 1023})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_views_status_is_200_when_type_known(self):
        t = RestrictedAreaTypeFactory()
        url = reverse('zoning:restrictedarea_type_layer', kwargs={'type_pk': t.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class RestrictedAreasSerializationTest(TestCase):

    def setUp(self):
        self.type_1 = RestrictedAreaTypeFactory(name="ABC")
        self.type_2 = RestrictedAreaTypeFactory(name="AAC")
        self.type_3 = RestrictedAreaTypeFactory(name="ABB")
        self.type_4 = RestrictedAreaTypeFactory(name="AAA")
        self.area_1 = RestrictedAreaFactory(area_type=self.type_1, name="aaa")
        self.area_2 = RestrictedAreaFactory(area_type=self.type_1, name="aab")
        self.area_3 = RestrictedAreaFactory(area_type=self.type_2, name="aaa")
        self.area_4 = RestrictedAreaFactory(area_type=self.type_2, name="aab")
        self.area_4 = RestrictedAreaFactory(area_type=self.type_3, name="aab")
        self.area_5 = RestrictedAreaFactory(area_type=self.type_3, name="aaa")
        self.area_6 = RestrictedAreaFactory(area_type=self.type_4, name="aba")
        self.area_7 = RestrictedAreaFactory(area_type=self.type_4, name="aca")
        self.area_8 = RestrictedAreaFactory(area_type=self.type_4, name="aaa")

    def test_restricted_areas_by_type_serizalization(self):
        """ Test restricted areas are sorted by type and ordered alphabetically within types
        """
        serizalized = restricted_areas_by_type()
        correct_data = json.dumps({
            "1": {"areas": [{"1": "ABC - aaa"}, {"2": "ABC - aab"}]},
            "2": {"areas": [{"3": "AAC - aaa"}, {"4": "AAC - aab"}]},
            "3": {"areas": [{"6": "ABB - aaa"}, {"5": "ABB - aab"}]},
            "4": {"areas": [{"9": "AAA - aaa"}, {"7": "AAA - aba"}, {"8": "AAA - aca"}]}
        })
        self.assertJSONEqual(serizalized, correct_data)

    def test_all_restricted_areas_serizalization(self):
        """ Test restricted areas are ordered alphabetically by type name then by area name
        """
        serizalized = all_restricted_areas()
        correct_data = json.dumps([
            {"9": "AAA - aaa"},
            {"7": "AAA - aba"},
            {"8": "AAA - aca"},
            {"3": "AAC - aaa"},
            {"4": "AAC - aab"},
            {"6": "ABB - aaa"},
            {"5": "ABB - aab"},
            {"1": "ABC - aaa"},
            {"2": "ABC - aab"}
        ])
        self.assertJSONEqual(serizalized, correct_data)
