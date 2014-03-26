from django.test import TestCase
from django.core.urlresolvers import reverse

from geotrek.authent.factories import TrekkingManagerFactory
from geotrek.tourism.models import DataSource, DATA_SOURCE_TYPES


class TourismViewsTests(TestCase):

    def setUp(self):
        self.source = DataSource.objects.create(title='S',
                                                url='http://source.com',
                                                type=DATA_SOURCE_TYPES.GEOJSON)
        user = TrekkingManagerFactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)

    def test_trekking_managers_can_access_data_sources_admin_site(self):
        url = reverse('admin:tourism_datasource_add')
        response = self.client.get(url)
        self.assertContains(response, DATA_SOURCE_TYPES.TOURINFRANCE)
