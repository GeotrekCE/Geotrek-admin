from django.test import TestCase
from django.core.urlresolvers import reverse
from caminae.authent.factories import PathManagerFactory
from caminae.maintenance.factories import InterventionFactory


class ViewsTest(TestCase):
    def test_status(self):
        # JSON layers do not require authent
        response = self.client.get(reverse("maintenance:intervention_layer"))
        self.assertEqual(response.status_code, 200)

    def test_crud_status(self):
        user = PathManagerFactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)
        
        response = self.client.get(reverse('maintenance:intervention_detail', args=[1234]))
        self.assertEqual(response.status_code, 404)
        
        i1 = InterventionFactory()
        response = self.client.get(i1.get_detail_url())
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(i1.get_update_url())
        self.assertEqual(response.status_code, 200)
        
        for url in [reverse('maintenance:intervention_add'), i1.get_update_url()]:
            # no data
            response = self.client.post(url)
            self.assertEqual(response.status_code, 200)
            
            bad_data = {'geom': 'doh!'}
            response = self.client.post(url, bad_data)
            self.assertEqual(response.status_code, 200)
            self.assertFormError(response, 'form', 'geom', u'Acune valeur g\xe9om\xe9trique fournie.')
            
            good_data = {
                'name': '',
                'structure': i1.structure.pk,
                'stake': '',
                'trail': '',
                'comments': '',
                'datasource': '',
                'valid': 'on',
                'geom': 'LINESTRING (0.0 0.0 0.0, 1.0 1.0 1.0)',
            }
            response = self.client.post(url, good_data)
            self.assertEqual(response.status_code, 302)

        response = self.client.get(i1.get_delete_url())
        self.assertEqual(response.status_code, 200)
