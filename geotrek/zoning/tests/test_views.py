from django.test import TestCase
from django.core.urlresolvers import reverse


class LandLayersViewsTest(TestCase):

    def test_views_status(self):
        for layer in ['city', 'restrictedarea', 'district']:
            url = reverse('zoning:%s_layer' % layer)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
