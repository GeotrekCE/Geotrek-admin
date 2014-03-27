import json

import mock
from django.test import TestCase
from django.core.urlresolvers import reverse

from geotrek.authent.factories import TrekkingManagerFactory
from geotrek.tourism.models import DataSource, DATA_SOURCE_TYPES


class TrekkingManagerTest(TestCase):
    def login(self):
        user = TrekkingManagerFactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)



class TourismAdminViewsTests(TrekkingManagerTest):

    def setUp(self):
        self.source = DataSource.objects.create(title='S',
                                                url='http://source.com',
                                                type=DATA_SOURCE_TYPES.GEOJSON)
        self.login()

    def test_trekking_managers_can_access_data_sources_admin_site(self):
        url = reverse('admin:tourism_datasource_changelist')
        response = self.client.get(url)
        self.assertContains(response, 'datasource/%s' % self.source.id)

    def test_datasource_title_is_translated(self):
        url = reverse('admin:tourism_datasource_add')
        response = self.client.get(url)
        self.assertContains(response, 'title_fr')


class DataSourceListViewTests(TrekkingManagerTest):
    def setUp(self):
        self.source = DataSource.objects.create(title='title',
                                                title_it='titolo',
                                                url='http://source.com',
                                                type=DATA_SOURCE_TYPES.GEOJSON)
        self.login()
        self.url = reverse('tourism:datasource_list_json')
        self.response = self.client.get(self.url)

    def tearDown(self):
        self.client.logout()

    def test_sources_are_listed_as_json(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response['Content-Type'], 'application/json')

    def test_sources_properties_are_provided(self):
        datasources = json.loads(self.response.content)
        self.assertEqual(len(datasources), 1)
        self.assertEqual(datasources[0]['id'], self.source.id)
        self.assertEqual(datasources[0]['url'], self.source.url)

    def test_sources_respect_request_language(self):
        response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='it-IT')
        self.assertEqual(response.status_code, 200)
        datasources = json.loads(response.content)
        self.assertEqual(datasources[0]['title'],
                         self.source.title_it)


class DataSourceViewTests(TrekkingManagerTest):
    def setUp(self):
        self.source = DataSource.objects.create(title='title',
                                                url='http://source.com',
                                                type=DATA_SOURCE_TYPES.GEOJSON)
        self.url = reverse('tourism:datasource_geojson', kwargs={'pk': self.source.pk})
        self.login()

    def tearDown(self):
        self.client.logout()

    def test_source_is_fetched_upon_view_call(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = '{}'
            self.client.get(self.url)
            mocked.assert_called_with(self.source.url)

    def test_empty_source_response_return_empty_data(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = '{}'
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            datasource = json.loads(response.content)
            self.assertEqual(datasource, {})

    def test_source_is_returned_as_geojson(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = '{"type": "foo"}'
            response = self.client.get(self.url)
            self.assertEqual(json.loads(response.content),
                             {'type': 'foo'})


class DataSourceTourInFranceViewTests(TrekkingManagerTest):
    def setUp(self):
        self.source = DataSource.objects.create(title='title',
                                                url='http://source.com',
                                                type=DATA_SOURCE_TYPES.TOURINFRANCE)
        self.url = reverse('tourism:datasource_geojson', kwargs={'pk': self.source.pk})
        self.login()

    def tearDown(self):
        self.client.logout()

    def test_source_is_returned_as_geojson_when_tourinfrance(self):
        with mock.patch('requests.get') as mocked:
            mocked().text = "<xml></xml>"
            response = self.client.get(self.url)
            geojson = json.loads(response.content)
            self.assertEqual(geojson['type'], 'FeatureCollection')
