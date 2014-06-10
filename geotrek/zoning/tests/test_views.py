from django.test import TestCase
from django.core.urlresolvers import reverse

from geotrek.zoning.factories import RestrictedAreaTypeFactory


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
