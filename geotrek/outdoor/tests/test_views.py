from geotrek.common.tests import CommonTest
from geotrek.outdoor.factories import SiteFactory
from geotrek.tourism.tests.test_views import PNG_BLACK_PIXEL
from unittest import mock


class SiteCustomViewTests(CommonTest):

    @mock.patch('mapentity.helpers.requests.get')
    def test_public_document_pdf(self, mocked):
        site = SiteFactory.create(published=True)
        url = '/api/en/sites/{pk}/slug.pdf'.format(pk=site.pk)
        mocked.return_value.status_code = 200
        mocked.return_value.content = PNG_BLACK_PIXEL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
