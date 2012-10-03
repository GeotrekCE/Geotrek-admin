# -*- coding: utf-8 -*-

import os
import shutil, StringIO, csv

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.test import LiveServerTestCase
from django.test.utils import override_settings
from django.test.testcases import to_list

from django.utils import html

from caminae.mapentity.forms import MapEntityForm


@override_settings(MEDIA_ROOT='/tmp/caminae-media')
class MapEntityTest(LiveServerTestCase):
    model = None
    modelfactory = None
    userfactory = None

    def setUp(self):
        if os.path.exists(settings.MEDIA_ROOT):
            self.tearDown()
        os.makedirs(settings.MEDIA_ROOT)

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def login(self):
        user = self.userfactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)

    def logout(self):
        self.client.logout()

    def get_bad_data(self):
        return {'topology': 'doh!'}, _(u'Topology is not valid.')

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

        # Document layer either
        obj = self.modelfactory.create()
        print obj.date_insert, obj.date_update
        # Will have to mock screenshot, though.
        with open(obj.get_map_image_path(), 'w') as f:
            f.write('This is fake PNG file')
        response = self.client.get(obj.get_document_url())
        self.assertEqual(response.status_code, 200)

    def test_bbox_filter(self):
        if self.model is None:
            return  # Abstract test should not run
        params = '?bbox=POLYGON((5+44+0%2C5+45+0%2C6+45+0%2C6+44+0%2C5+44+0))'
        response = self.client.get(self.model.get_jsonlist_url()+params)
        self.assertEqual(response.status_code, 200)

    def test_basic_format(self):
        if self.model is None:
            return  # Abstract test should not run
        self.login()
        self.modelfactory.create()
        for fmt in ('csv', 'shp', 'gpx'):
            response = self.client.get(self.model.get_format_list_url() + '?format=' + fmt)
            self.assertEqual(response.status_code, 200, u"")

    def test_no_html_in_csv(self):
        if self.model is None:
            return  # Abstract test should not run

        self.login()

        self.modelfactory.create()

        fmt = 'csv'
        response = self.client.get(self.model.get_format_list_url() + '?format=' + fmt)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')

        # Read the csv
        lines = list(csv.reader(StringIO.StringIO(response.content), delimiter=','))

        # There should be one more line in the csv than in the items: this is the header line
        self.assertEqual(len(lines), self.model.objects.all().count() + 1)

        for line in lines:
            for col in line:
                # the col should not contains any html tags
                self.assertEquals(force_unicode(col), html.strip_tags(col))

    def test_crud_status(self):
        if self.model is None:
            return  # Abstract test should not run

        self.login()
        
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

            form = None
            for c in response.context:
                _form = c.get('form')
                if _form and isinstance(_form, MapEntityForm):
                    form = _form
                    break

            if not form:
                self.fail(u'Could not find form')

            fields_errors = form.errors[bad_data.keys()[0]]
            for err in to_list(form_error):
                self.assertTrue(err in fields_errors)

            response = self.client.post(url, self.get_good_data())
            if response.status_code != 302:
                self.assertEqual(form.errors, [])  # this will show form errors
                
            self.assertEqual(response.status_code, 302)  # success, redirects to detail view

        response = self.client.get(obj.get_delete_url())
        self.assertEqual(response.status_code, 200)

    def test_map_image(self):
        if self.model is None:
            return  # Abstract test should not run

        obj = self.modelfactory.create()
        
        # Initially, map image does not exists
        self.assertFalse(os.path.exists(obj.get_map_image_path()))
        # TODO: test disabled since not working on CI server
        # obj.prepare_map_image(self.live_server_url)
        # self.assertTrue(os.path.exists(obj.get_map_image_path()))
