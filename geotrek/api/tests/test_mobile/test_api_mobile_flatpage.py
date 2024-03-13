from django.urls import reverse
from django.test.testcases import TestCase
from django.utils import translation

from geotrek.flatpages.tests.factories import FlatPageFactory, MenuItemFactory
from geotrek.flatpages.models import FlatPage

FLATPAGE_DETAIL_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'title', 'external_url', 'content'
])


class FlatPageTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        translation.activate('fr')
        cls.flatpage = FlatPageFactory.create(published_fr=True)
        cls.menu_item = MenuItemFactory.create(page=cls.flatpage)
        flatpage2 = FlatPageFactory.create(published_fr=True)
        MenuItemFactory.create(page=flatpage2)

    def get_flatpage_list(self, params=None):
        return self.client.get(reverse('apimobile:flatpage-list'), params, HTTP_ACCEPT_LANGUAGE='fr')

    def get_flatpage_detail(self, id_flatpage, params=None):
        return self.client.get(reverse('apimobile:flatpage-detail', args=(id_flatpage,)),
                               params, HTTP_ACCEPT_LANGUAGE='fr')

    def test_flatpage_list(self):
        response = self.get_flatpage_list()
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response), 2)
        self.assertEqual(json_response[0].get('title'), FlatPage.objects.first().title)

    def test_flatpage_detail(self):
        response = self.get_flatpage_detail(self.flatpage.pk)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()),
                         FLATPAGE_DETAIL_PROPERTIES_JSON_STRUCTURE)
        self.assertEqual(json_response.get('content'), self.flatpage.content)
        self.assertEqual(json_response.get('title'), self.flatpage.title)

    def tearDown(self):
        translation.deactivate()
