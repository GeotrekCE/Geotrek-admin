# -*- coding: utf-8 -*-
import csv
import hashlib
import logging
import os
import shutil
import time
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote

from freezegun import freeze_time
from io import StringIO
from unittest.mock import patch

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, LiveServerTestCase
from django.test.testcases import to_list
from django.test.utils import override_settings
from django.utils import html
from django.utils.encoding import force_str
from django.utils.http import http_date
from django.utils.timezone import utc
from django.utils.translation import gettext_lazy as _

from ..factories import SuperUserFactory
from ..forms import MapEntityForm
from ..helpers import smart_urljoin
from ..registry import app_settings


class AdjustDebugLevel():
    def __init__(self, name, level):
        self.logger = logging.getLogger(name)
        self.old_level = self.logger.level
        self.new_level = level

    def __enter__(self):
        self.logger.setLevel(self.new_level)

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.setLevel(self.old_level)


@override_settings(MEDIA_ROOT='/tmp/mapentity-media')
class MapEntityTest(TestCase):
    model = None
    modelfactory = None
    userfactory = None
    api_prefix = '/api/'
    expected_json_geom = {}
    maxDiff = None

    def get_expected_json_attrs(self):
        return {}

    def setUp(self):
        if os.path.exists(settings.MEDIA_ROOT):
            self.tearDown()
        os.makedirs(settings.MEDIA_ROOT)

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def login(self):
        self.user = self.userfactory(password='booh')
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def logout(self):
        self.client.logout()

    def get_bad_data(self):
        return {'geom': 'doh!'}, _('Invalid geometry value.')

    def get_good_data(self):
        raise NotImplementedError()

    def get_form(self, response):
        form = None
        for c in response.context:
            _form = c.get('form')
            if _form and isinstance(_form, MapEntityForm):
                form = _form
                break

        if not form:
            self.fail(u'Could not find form')
        return form

    def test_status(self):
        if self.model is None:
            return  # Abstract test should not run

        # Make sure database is not empty for this model
        for i in range(30):
            self.modelfactory.create()

        self.login()
        response = self.client.get(self.model.get_layer_url())
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.model.get_jsonlist_url())
        self.assertEqual(response.status_code, 200)

    @patch('mapentity.helpers.requests')
    def test_document_export(self, mock_requests):
        if self.model is None:
            return  # Abstract test should not run

        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = b'<p id="properties">Mock</p>'

        self.login()
        obj = self.modelfactory.create()
        response = self.client.get(obj.get_document_url())
        self.assertEqual(response.status_code, 200)

    def test_bbox_filter(self):
        if self.model is None:
            return  # Abstract test should not run
        self.login()
        params = '?tiles=5,16,11'
        # If no objects exist, should not fail.
        response = self.client.get(self.model.get_jsonlist_url() + params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['map_obj_pk'], [])
        # If object exists, either :)
        obj = self.modelfactory.create()
        response = self.client.get(self.model.get_jsonlist_url() + params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['map_obj_pk'], [obj.pk])
        # If bbox is invalid, it should return all
        allresponse = self.client.get(self.model.get_jsonlist_url())
        self.assertEqual(allresponse.json()['map_obj_pk'], [obj.pk])
        params = '?tiles=a,b,c'
        with AdjustDebugLevel('django.contrib.gis', logging.CRITICAL):
            response = self.client.get(self.model.get_jsonlist_url() + params)
        self.assertEqual(response.status_code, 200)
        response.content = allresponse.content
        params = '?tiles=5,19,11'
        # Out of box.
        response = self.client.get(self.model.get_jsonlist_url() + params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['map_obj_pk'], [])

    def test_callback_jsonlist(self):
        if self.model is None:
            return  # Abstract test should not run
        self.login()
        params = '?callback=json_decode'
        # If no objects exist, should not fail.
        response = self.client.get(self.model.get_jsonlist_url() + params)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'json_decode(', response.content)

    def test_basic_format(self):
        if self.model is None:
            return  # Abstract test should not run
        self.login()
        self.modelfactory.create()
        for fmt in ('csv', 'shp', 'gpx'):
            response = self.client.get(self.model.get_format_list_url() + '?format=' + fmt)
            self.assertEqual(response.status_code, 200, u"")

    def test_gpx_elevation(self):
        if self.model is None:
            return  # Abstract test should not run
        self.login()
        obj = self.modelfactory.create()
        response = self.client.get(self.model.get_format_list_url() + '?format=gpx')
        parsed = BeautifulSoup(response.content, 'lxml')
        if hasattr(obj, 'geom_3d'):
            self.assertGreater(len(parsed.findAll('ele')), 0)
        else:
            self.assertEqual(len(parsed.findAll('ele')), 0)

    def test_no_basic_format_fail(self):
        if self.model is None:
            return  # Abstract test should not run
        self.login()
        self.modelfactory.create()

        response = self.client.get(self.model.get_format_list_url() + '?format=')
        self.assertEqual(response.status_code, 400)

    def test_no_html_in_csv(self):
        if self.model is None:
            return  # Abstract test should not run

        self.login()

        self.modelfactory.create()

        fmt = 'csv'
        response = self.client.get(self.model.get_format_list_url() + '?format=' + fmt)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')

        # Read the csv
        lines = list(csv.reader(StringIO(response.content.decode("utf-8")), delimiter=','))

        # There should be one more line in the csv than in the items: this is the header line
        self.assertEqual(len(lines), self.model.objects.all().count() + 1)

        for line in lines:
            for col in line:
                # the col should not contains any html tags
                self.assertEqual(force_str(col), html.strip_tags(force_str(col)))

    def _post_form(self, url):
        # no data
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        bad_data, form_error = self.get_bad_data()
        with AdjustDebugLevel('django.contrib.gis', logging.CRITICAL):
            response = self.client.post(url, bad_data)
        self.assertEqual(response.status_code, 200)

        form = self.get_form(response)

        fields_errors = form.errors[list(bad_data.keys())[0]]
        form_errors = to_list(form_error)
        for err in form_errors:
            self.assertTrue(u"{}".format(err) in fields_errors,
                            u"'%s' not in %s" % (err, fields_errors))

        response = self.client.post(url, self.get_good_data())
        if response.status_code != 302:
            form = self.get_form(response)
            self.assertFalse(form.errors)  # this will show form errors

        self.assertEqual(response.status_code, 302)  # success, redirects to detail view

    def _get_add_url(self):
        return self.model.get_add_url()

    def _post_add_form(self):
        self._post_form(self._get_add_url())

    def _post_update_form(self, obj):
        self._post_form(obj.get_update_url())

    def _check_update_geom_permission(self, response):
        if self.user.has_perm('{app}.change_geom_{model}'.format(app=self.model._meta.app_label,
                                                                 model=self.model._meta.model_name)):
            self.assertIn(b'.modifiable = true;', response.content)
        else:
            self.assertIn(b'.modifiable = false;', response.content)

    def test_crud_status(self):
        if self.model is None:
            return  # Abstract test should not run

        self.login()

        obj = self.modelfactory()

        response = self.client.get(obj.get_list_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(obj.get_detail_url().replace(str(obj.pk), '1234567890'))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(obj.get_detail_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(obj.get_update_url())
        self.assertEqual(response.status_code, 200)
        self._post_update_form(obj)
        self._check_update_geom_permission(response)

        response = self.client.get(obj.get_delete_url())
        self.assertEqual(response.status_code, 200)

        url = obj.get_detail_url()
        obj.delete()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        self._post_add_form()

        # Test to update without login
        self.logout()

        obj = self.modelfactory()

        response = self.client.get(self.model.get_add_url())
        self.assertEqual(response.status_code, 302)
        response = self.client.get(obj.get_update_url())
        self.assertEqual(response.status_code, 302)

    def test_formfilter_in_list_context(self):
        if self.model is None:
            return  # Abstract test should not run
        self.login()
        response = self.client.get(self.model.get_list_url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['filterform'] is not None)

    """

        REST API

    """

    @freeze_time("2020-03-17")
    def test_api_list_for_model(self):
        if self.get_expected_json_attrs is None:
            return
        if self.model is None:
            return  # Abstract test should not run
        self.login()

        self.obj = self.modelfactory.create()
        list_url = '{api_prefix}{modelname}s.json'.format(api_prefix=self.api_prefix,
                                                          modelname=self.model._meta.model_name)
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        content_json = response.json()
        if hasattr(self, 'length'):
            length = content_json[0].pop('length')
            self.assertAlmostEqual(length, self.length)
        self.assertEqual(content_json, [{'id': self.obj.pk, **self.get_expected_json_attrs()}])

    @freeze_time("2020-03-17")
    def test_api_geojson_list_for_model(self):
        if self.get_expected_json_attrs is None:
            return
        if self.model is None:
            return  # Abstract test should not run
        self.login()

        self.obj = self.modelfactory.create()
        list_url = '{api_prefix}{modelname}s.geojson'.format(api_prefix=self.api_prefix,
                                                             modelname=self.model._meta.model_name)
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        content_json = response.json()
        if hasattr(self, 'length'):
            length = content_json['features'][0]['properties'].pop('length')
            self.assertAlmostEqual(length, self.length)
        self.assertEqual(content_json, {
            'type': 'FeatureCollection',
            'features': [{
                'id': self.obj.pk,
                'type': 'Feature',
                'geometry': self.expected_json_geom,
                'properties': self.get_expected_json_attrs(),
            }],
        })

    @freeze_time("2020-03-17")
    def test_api_detail_for_model(self):
        if self.get_expected_json_attrs is None:
            return
        if self.model is None:
            return  # Abstract test should not run
        self.login()

        self.obj = self.modelfactory.create()
        detail_url = '{api_prefix}{modelname}s/{id}'.format(api_prefix=self.api_prefix,
                                                            modelname=self.model._meta.model_name,
                                                            id=self.obj.pk)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)

        content_json = response.json()
        if hasattr(self, 'length'):
            length = content_json.pop('length')
            self.assertAlmostEqual(length, self.length)
        self.assertEqual(content_json, {'id': self.obj.pk, **self.get_expected_json_attrs()})

    @freeze_time("2020-03-17")
    def test_api_geojson_detail_for_model(self):
        if self.get_expected_json_attrs is None:
            return
        if self.model is None:
            return  # Abstract test should not run
        self.login()

        self.obj = self.modelfactory.create()
        detail_url = '{api_prefix}{modelname}s/{id}.geojson'.format(api_prefix=self.api_prefix,
                                                                    modelname=self.model._meta.model_name,
                                                                    id=self.obj.pk)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        content_json = response.json()
        if hasattr(self, 'length'):
            length = content_json['properties'].pop('length')
            self.assertAlmostEqual(length, self.length)
        self.assertEqual(content_json, {
            'id': self.obj.pk,
            'type': 'Feature',
            'geometry': self.expected_json_geom,
            'properties': self.get_expected_json_attrs(),
        })


class MapEntityLiveTest(LiveServerTestCase):
    model = None
    userfactory = None
    modelfactory = None

    def setUp(self):
        app_settings['SENDFILE_HTTP_HEADER'] = None

    def _pre_setup(self):
        # Workaround https://code.djangoproject.com/ticket/10827
        ContentType.objects.clear_cache()
        return super(MapEntityLiveTest, self)._pre_setup()

    def url_for(self, path):
        return smart_urljoin(self.live_server_url, path)

    def login(self):
        user = self.userfactory(password='booh')
        login_url = self.url_for('/login/')
        response = self.client.get(login_url,
                                   allow_redirects=False)
        csrftoken = response.cookies['csrftoken']
        response = self.client.post(login_url,
                                    {'username': user.username,
                                     'password': 'booh',
                                     'csrfmiddlewaretoken': csrftoken},
                                    allow_redirects=False)
        self.assertEqual(response.status_code, 302)

    @patch('mapentity.models.MapEntityMixin.latest_updated')
    def test_geojson_cache(self, latest_updated):
        if self.model is None:
            return  # Abstract test should not run

        self.login()
        self.modelfactory.create()
        latest_updated.return_value = datetime.utcnow().replace(tzinfo=utc)

        latest = self.model.latest_updated()
        geojson_layer_url = self.url_for(self.model.get_layer_url())

        response = self.client.get(geojson_layer_url, allow_redirects=False)
        self.assertEqual(response.status_code, 200)

        # Without headers to cache
        lastmodified = response.get('Last-Modified')
        cachecontrol = response.get('Cache-control')
        hasher = hashlib.md5()
        hasher.update(response.content)
        md5sum = hasher.digest()
        self.assertNotEqual(lastmodified, None)
        self.assertCountEqual(cachecontrol.split(', '), ('must-revalidate', 'max-age=0'))

        # Try again, check that nothing changed
        time.sleep(1.1)
        self.assertEqual(latest, self.model.latest_updated())
        response = self.client.get(geojson_layer_url)
        self.assertEqual(lastmodified, response.get('Last-Modified'))
        new_hasher = hashlib.md5()
        new_hasher.update(response.content)
        self.assertEqual(md5sum, new_hasher.digest())

        # Create a new object
        time.sleep(1.1)  # wait some time, last-modified has precision in seconds
        self.modelfactory.create()
        latest_updated.return_value = datetime.utcnow().replace(tzinfo=utc)

        self.assertNotEqual(latest, self.model.latest_updated())
        response = self.client.get(geojson_layer_url)
        # Check that last modified and content changed
        self.assertNotEqual(lastmodified, response.get('Last-Modified'))
        new_hasher = hashlib.md5()
        new_hasher.update(response.content)
        self.assertNotEqual(md5sum, new_hasher.digest())

        # Ask again with headers, and expect a 304 status (not changed)
        lastmodified = response.get('Last-Modified')
        response = self.client.get(geojson_layer_url, HTTP_IF_MODIFIED_SINCE=lastmodified)
        self.assertEqual(response.status_code, 304)

        # Ask again with headers in the past, and expect a 200
        response = self.client.get(geojson_layer_url, HTTP_IF_MODIFIED_SINCE=http_date(1000))
        self.assertEqual(response.status_code, 200)
        new_hasher = hashlib.md5()
        new_hasher.update(response.content)
        self.assertNotEqual(md5sum, new_hasher.digest())

    @patch('mapentity.helpers.requests')
    def test_map_image(self, mock_requests):
        if self.model is None:
            return  # Abstract test should not run

        SuperUserFactory.create(username='Superuser', password='booh')
        self.client.login(username='Superuser', password='booh')

        obj = self.modelfactory.create(geom='POINT(0 0)')

        # Initially, map image does not exists
        image_path = obj.get_map_image_path()
        if os.path.exists(image_path):
            os.remove(image_path)
        self.assertFalse(os.path.exists(image_path))

        # Mock Screenshot response
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = b'*' * 100

        response = self.client.get(obj.map_image_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.exists(image_path))

        mapimage_url = '%s%s?context' % (self.live_server_url, obj.get_detail_url())
        screenshot_url = 'http://0.0.0.0:8001/?url=%s' % quote(mapimage_url)
        url_called = mock_requests.get.call_args_list[0]
        self.assertTrue(url_called.startswith(screenshot_url))

    @patch('mapentity.helpers.requests')
    def test_map_image_as_anonymous_user(self, mock_requests):
        if self.model is None:
            return  # Abstract test should not run

        obj = self.modelfactory.create(geom='POINT(0 0)')

        # Mock Screenshot response
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = b'*' * 100

        response = self.client.get(obj.map_image_url)
        self.assertEqual(response.status_code, 200 if obj.is_public() else 403)

    def tearDown(self):
        app_settings['SENDFILE_HTTP_HEADER'] = None
