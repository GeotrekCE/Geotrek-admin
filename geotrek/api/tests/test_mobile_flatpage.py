from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase
from django.utils import translation

from geotrek.flatpages.factories import FlatPageFactory
from geotrek.flatpages.models import FlatPage

FLATPAGE_DETAIL_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'title', 'external_url', 'content'
])


class FlatPageAdministratorTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        translation.activate('fr')
        cls.flatpage = FlatPageFactory.create(published_fr=True)
        FlatPageFactory.create(published_fr=True)
        cls.administrator = User.objects.create(username="administrator", is_superuser=True,
                                                is_staff=True, is_active=True)
        cls.administrator.set_password('administrator')
        cls.administrator.save()
        cls.administrator.refresh_from_db()

    def get_flatpage_list(self, params=None):
        return self.client.get(reverse('apimobile:flatpage-list'), params, HTTP_ACCEPT_LANGUAGE='fr')

    def get_flatpage_detail(self, id_flatpage, params=None):
        return self.client.get(reverse('apimobile:flatpage-detail', args=(id_flatpage,)),
                               params, HTTP_ACCEPT_LANGUAGE='fr')

    def test_flatpage_list_administrator(self):
        self.client.login(username="administrator", password="administrator")
        response = self.get_flatpage_list()
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response), 2)
        self.assertEqual(json_response[0].get('title'), FlatPage.objects.first().title)

    def test_flatpage_detail_administrator(self):
        self.client.login(username="administrator", password="administrator")
        response = self.get_flatpage_detail(self.flatpage.pk)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()),
                         FLATPAGE_DETAIL_PROPERTIES_JSON_STRUCTURE)
        self.assertEqual(json_response.get('content'), self.flatpage.content)
        self.assertEqual(json_response.get('title'), self.flatpage.title)

    def tearDown(self):
        translation.deactivate()


class FlatPageAnonymousTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        translation.activate('fr')
        cls.flatpage = FlatPageFactory.create(published_fr=True)
        FlatPageFactory.create(published_fr=True)

    def get_flatpage_list(self, params=None):
        return self.client.get(reverse('apimobile:flatpage-list'), params, HTTP_ACCEPT_LANGUAGE='fr')

    def get_flatpage_detail(self, id_flatpage, params=None):
        return self.client.get(reverse('apimobile:flatpage-detail', args=(id_flatpage,)),
                               params, HTTP_ACCEPT_LANGUAGE='fr')

    def test_flatpage_list_administrator(self):
        response = self.get_flatpage_list()
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response), 2)
        self.assertEqual(json_response[0].get('title'), FlatPage.objects.first().title)

    def test_flatpage_detail_administrator(self):
        response = self.get_flatpage_detail(self.flatpage.pk)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()),
                         FLATPAGE_DETAIL_PROPERTIES_JSON_STRUCTURE)
        self.assertEqual(json_response.get('content'), self.flatpage.content)
        self.assertEqual(json_response.get('title'), self.flatpage.title)

    def tearDown(self):
        translation.deactivate()
