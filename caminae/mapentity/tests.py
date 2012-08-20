from django.test import TestCase


class MapEntityTest(TestCase):
    model = None
    modelfactory = None
    userfactory = None

    def get_bad_data(self):
        return {'geom': 'doh!'}, u'Topology is not valid.'

    def get_good_data(self):
        raise NotImplementedError()

    def test_status(self):
        if self.model is None:
            return  # Abstract test should not run

        # Make sure database is not empty for this model
        for i in range(30):
            self.modelfactory.create()

        # JSON layers do not require authent
        response = self.client.get(self.model.get_layer_url())
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.model.get_jsonlist_url())
        self.assertEqual(response.status_code, 200)

    def test_bbox_filter(self):
        if self.model is None:
            return  # Abstract test should not run
        params = '?bbox=POLYGON((5+44+0%2C5+45+0%2C6+45+0%2C6+44+0%2C5+44+0))'
        response = self.client.get(self.model.get_jsonlist_url()+params)
        self.assertEqual(response.status_code, 200)

    def test_crud_status(self):
        if self.model is None:
            return  # Abstract test should not run

        user = self.userfactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)
        
        obj = self.modelfactory()
        response = self.client.get(obj.get_detail_url().replace(str(obj.pk), '1234567890'))
        self.assertEqual(response.status_code, 404)
        
        response = self.client.get(obj.get_detail_url())
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(obj.get_update_url())
        self.assertEqual(response.status_code, 200)

        for url in [self.model.get_add_url(), obj.get_update_url()]:
            # no data
            response = self.client.post(url)
            self.assertEqual(response.status_code, 200)
            
            bad_data, form_error = self.get_bad_data()
            response = self.client.post(url, bad_data)
            self.assertEqual(response.status_code, 200)
            self.assertFormError(response, 'form', bad_data.keys()[0], form_error)

            response = self.client.post(url, self.get_good_data())
            if response.status_code != 302:
                self.assertEqual(response.context['form'].errors, [])  # this will show form errors
                
            self.assertEqual(response.status_code, 302)  # success, redirects to detail view

        response = self.client.get(obj.get_delete_url())
        self.assertEqual(response.status_code, 200)
