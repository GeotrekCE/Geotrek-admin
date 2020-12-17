from django.test import TestCase
from geotrek.common.factories import RecordSourceFactory, TargetPortalFactory
from geotrek.outdoor.factories import SiteFactory
from geotrek.tourism.tests.test_views import PNG_BLACK_PIXEL
from unittest import mock


class SiteCustomViewTests(TestCase):
    @mock.patch('mapentity.helpers.requests.get')
    def test_public_document_pdf(self, mocked):
        site = SiteFactory.create(published=True)
        url = '/api/en/sites/{pk}/slug.pdf'.format(pk=site.pk)
        mocked.return_value.status_code = 200
        mocked.return_value.content = PNG_BLACK_PIXEL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_api_filters(self):
        SiteFactory.create(name='site1', published=False)
        SiteFactory.create(name='site2', published=True)
        site3 = SiteFactory.create(name='site3', published=True)
        site3.source.add(RecordSourceFactory.create(name='source1'))
        site3.portal.add(TargetPortalFactory.create(name='portal1'))

        response1 = self.client.get('/api/en/sites.json')
        self.assertEqual(len(response1.json()), 2)
        self.assertEqual(set((site['name'] for site in response1.json())), set(('site2', 'site3')))

        response2 = self.client.get('/api/en/sites.json?source=source1')
        self.assertEqual(len(response2.json()), 1)
        self.assertEqual(response2.json()[0]['name'], 'site3')

        response3 = self.client.get('/api/en/sites.json?portal=portal1')
        self.assertEqual(len(response3.json()), 2)
        self.assertEqual(set((site['name'] for site in response3.json())), set(('site2', 'site3')))

        response4 = self.client.get('/api/en/sites.json?portal=portalX')
        self.assertEqual(len(response4.json()), 1)
        self.assertEqual(response4.json()[0]['name'], 'site2')
