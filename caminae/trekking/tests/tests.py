from django.test import TestCase
from django.core.urlresolvers import reverse
from caminae.authent.factories import TrekkingManagerFactory
from caminae.trekking.factories import TrekFactory


class ViewsTest(TestCase):
    def test_status(self):
        response = self.client.get(reverse("trekking:trekking_layer"))
        self.assertEqual(response.status_code, 200)

    def test_crud_status(self):
        user = TrekkingManagerFactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)
        
        response = self.client.get(reverse('trekking:trek_detail', args=[1234]))
        self.assertEqual(response.status_code, 404)
        
        t = TrekFactory()
        response = self.client.get(t.get_detail_url())
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(t.get_update_url())
        self.assertEqual(response.status_code, 200)
        
        for url in [reverse('trekking:trek_add'), t.get_update_url()]:
            response = self.client.post(url)
            self.assertEqual(response.status_code, 200)
            
            bad_data = {'geom': 'doh!'}
            response = self.client.post(url, bad_data)
            self.assertEqual(response.status_code, 200)
            self.assertFormError(response, 'form', 'geom', u'Acune valeur g\xe9om\xe9trique fournie.')

            good_data = {
                'name': 'test',
                'geom': 'POINT (0.0 0.0 0.0)',
            }
            response = self.client.post(url, good_data)
            self.assertEqual(response.status_code, 302)  # success, redirects to detail view

        response = self.client.get(t.get_delete_url())
        self.assertEqual(response.status_code, 200)
