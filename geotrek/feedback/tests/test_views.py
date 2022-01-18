import json
from datetime import datetime
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Permission
from django.core import mail
from django.core.cache import caches
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from mapentity.tests.factories import SuperUserFactory, UserFactory
from rest_framework.test import APIClient

from geotrek.common.tests import CommonTest, TranslationResetMixin
from geotrek.common.utils.testdata import (get_dummy_uploaded_file,
                                           get_dummy_uploaded_image,
                                           get_dummy_uploaded_image_svg)
from geotrek.feedback import models as feedback_models
from geotrek.feedback.tests import factories as feedback_factories


class ReportViewsetMailSend(TestCase):

    @override_settings(SURICATE_REPORT_SETTINGS={"URL": "http://suricate.example.com",
                                                 "ID_ORIGIN": "geotrek",
                                                 "PRIVATE_KEY_CLIENT_SERVER": "",
                                                 "PRIVATE_KEY_SERVER_CLIENT": "",
                                                 "AUTH": ("", "")})
    @override_settings(SURICATE_REPORT_ENABLED=True)
    @override_settings(SURICATE_MANAGEMENTT_ENABLED=False)
    @mock.patch("geotrek.feedback.helpers.requests.post")
    def test_mail_send_on_request(self, mocked_post):
        mock_response = mock.Mock()
        mock_response.content = json.dumps({"code_ok": 'true'}).encode()
        mock_response.status_code = 200
        mocked_post.return_value = mock_response
        self.client.post(
            '/api/en/reports/report',
            {
                'geom': '{\"type\":\"Point\",\"coordinates\":[4.3728446995373815,43.856935212211454]}',
                'email': 'test@geotrek.local',
                'comment': 'Test comment',
                'activity': feedback_factories.ReportActivityFactory.create().pk,
                'problem_magnitude': feedback_factories.ReportProblemMagnitudeFactory.create().pk,
            })
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, "Geotrek : Signal a mistake")
        self.assertIn("We acknowledge receipt of your feedback", mail.outbox[1].body)
        self.assertEqual(mail.outbox[1].from_email, settings.DEFAULT_FROM_EMAIL)


class ReportSerializationOptimizeTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()
        cls.classified_status = feedback_factories.ReportStatusFactory(identifier='classified', label="Classé sans suite")
        cls.filed_status = feedback_factories.ReportStatusFactory(identifier='filed', label="Classé sans suite")
        cls.classified_report_1 = feedback_factories.ReportFactory(status=cls.classified_status)
        cls.classified_report_2 = feedback_factories.ReportFactory(status=cls.classified_status)
        cls.classified_report_3 = feedback_factories.ReportFactory(status=cls.classified_status)
        cls.filed_report = feedback_factories.ReportFactory(status=cls.filed_status)

    def setUp(cls):
        cls.client.force_login(cls.user)

    def test_report_layer_cache(self):
        """
        This test check report's per status cache work independently
        """
        cache = caches[settings.MAPENTITY_CONFIG['GEOJSON_LAYERS_CACHE_BACKEND']]

        # There are 5 queries to get layer
        with self.assertNumQueries(5):
            response = self.client.get("/api/report/report.geojson?_status_id=classified")
        self.assertEqual(len(response.json()['features']), 3)

        # We check the content was created and cached
        last_update_status = feedback_models.Report.latest_updated_by_status("classified")
        geojson_lookup_status = 'en_report_%s_classified_json_layer' % last_update_status.isoformat()
        content_per_status = cache.get(geojson_lookup_status)

        self.assertEqual(response.content, content_per_status)

        # We have 1 less query because the generation of report was cached
        with self.assertNumQueries(4):
            self.client.get("/api/report/report.geojson?_status_id=classified")

        self.classified_report_4 = feedback_factories.ReportFactory(status=self.classified_status)

        # Cache is updated when we add a report
        with self.assertNumQueries(5):
            self.client.get("/api/report/report.geojson?_status_id=classified")

        self.filed_report = feedback_factories.ReportFactory(status=self.filed_status)


class ReportViewsTest(CommonTest):
    model = feedback_models.Report
    modelfactory = feedback_factories.ReportFactory
    userfactory = SuperUserFactory
    expected_json_geom = {
        'type': 'Point',
        'coordinates': [3.0, 46.5],
    }
    extra_column_list = ['email', 'comment', 'advice']

    def get_expected_json_attrs(self):
        return {
            'activity': self.obj.activity.pk,
            'category': self.obj.category.pk,
            'comment': self.obj.comment,
            'related_trek': None,
            'email': self.obj.email,
            'status': self.obj.status_pk,
            'problem_magnitude': self.obj.problem_magnitude.pk
        }

    def get_bad_data(self):
        return {'geom': 'FOO'}, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'geom': '{"type": "Point", "coordinates": [0, 0]}',
            'email': 'yeah@you.com',
            'activity': feedback_factories.ReportActivityFactory.create().pk,
            'problem_magnitude': feedback_factories.ReportProblemMagnitudeFactory.create().pk,
        }

    def test_good_data_with_name(self):
        """Test report created if `name` in data"""
        data = self.get_good_data()
        data['name'] = 'Anonymous'
        self.login()
        response = self.client.post(self._get_add_url(), data)
        self.assertEqual(response.status_code, 302)
        obj = self.model.objects.last()
        self.assertEqual(obj.email, data['email'])
        self.logout()

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
        # No delete mixin
        self.assertEqual(response.status_code, 200)

        self._post_add_form()

        # Test to update without login
        self.logout()

        obj = self.modelfactory()

        response = self.client.get(self.model.get_add_url())
        self.assertEqual(response.status_code, 302)
        response = self.client.get(obj.get_update_url())
        self.assertEqual(response.status_code, 302)

    def test_custom_columns_mixin_on_list(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={'feedback_view': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}List')().columns,
                             ['id', 'email', 'activity', 'email', 'comment', 'advice'])

    def test_custom_columns_mixin_on_export(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={'feedback_export': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}FormatList')().columns,
                             ['id', 'email', 'comment', 'advice'])


class BaseAPITest(TestCase):
    def setUp(self):
        self.user = UserFactory(password='booh')
        perm = Permission.objects.get_by_natural_key('add_report', 'feedback', 'report')
        self.user.user_permissions.add(perm)

        self.login_url = '/login/'

    def login(self):
        response = self.client.get(self.login_url)
        csrftoken = response.cookies.get('csrftoken', '')
        response = self.client.post(self.login_url,
                                    {'username': self.user.username,
                                     'password': 'booh',
                                     'csrfmiddlewaretoken': csrftoken},
                                    allow_redirects=False)
        self.assertEqual(response.status_code, 302)


class CreateReportsAPITest(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.add_url = '/api/en/reports/report'
        self.data = {
            'geom': '{"type": "Point", "coordinates": [3, 46.5]}',
            'email': 'yeah@you.com',
            'activity': feedback_factories.ReportActivityFactory.create().pk,
            'problem_magnitude': feedback_factories.ReportProblemMagnitudeFactory.create().pk,
        }

    def post_report_data(self, data):
        client = APIClient()
        response = client.post(self.add_url, data=data,
                               allow_redirects=False)
        self.assertEqual(response.status_code, 201)

    def test_reports_can_be_created_using_post(self):
        self.post_report_data(self.data)
        self.assertTrue(feedback_models.Report.objects.filter(email='yeah@you.com').exists())
        report = feedback_models.Report.objects.get()
        self.assertAlmostEqual(report.geom.x, 700000)
        self.assertAlmostEqual(report.geom.y, 6600000)

    def test_reports_can_be_created_without_geom(self):
        self.data.pop('geom')
        self.post_report_data(self.data)
        self.assertTrue(feedback_models.Report.objects.filter(email='yeah@you.com').exists())

    def test_reports_with_file(self):
        self.data['file'] = get_dummy_uploaded_file()
        self.data['csv'] = get_dummy_uploaded_image_svg()
        self.data['image'] = get_dummy_uploaded_image()
        self.post_report_data(self.data)
        self.assertTrue(feedback_models.Report.objects.filter(email='yeah@you.com').exists())
        report = feedback_models.Report.objects.get()
        self.assertEqual(report.attachments.count(), 3)


class ListCategoriesTest(TranslationResetMixin, BaseAPITest):
    def setUp(self):
        super().setUp()
        self.cat = feedback_factories.ReportCategoryFactory(label_it='Obstaculo')

    def test_categories_can_be_obtained_as_json(self):
        response = self.client.get('/api/en/feedback/categories.json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data[0]['id'], self.cat.id)
        self.assertEqual(data[0]['label'], self.cat.label)

    def test_categories_are_translated(self):
        response = self.client.get('/api/it/feedback/categories.json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data[0]['label'], self.cat.label_it)


class ListOptionsTest(TranslationResetMixin, BaseAPITest):
    def setUp(self):
        super().setUp()
        self.activity = feedback_factories.ReportActivityFactory(label_it='Hiking')
        self.cat = feedback_factories.ReportCategoryFactory(label_it='Obstaculo')
        self.pb_magnitude = feedback_factories.ReportProblemMagnitudeFactory(label_it='Possible')

    def test_options_can_be_obtained_as_json(self):
        response = self.client.get('/api/en/feedback/options.json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['activities'][0]['id'], self.activity.id)
        self.assertEqual(data['activities'][0]['label'], self.activity.label)
        self.assertEqual(data['categories'][0]['id'], self.cat.id)
        self.assertEqual(data['categories'][0]['label'], self.cat.label)
        self.assertEqual(data['magnitudeProblems'][0]['id'], self.pb_magnitude.id)
        self.assertEqual(data['magnitudeProblems'][0]['label'], self.pb_magnitude.label)

    def test_options_are_translated(self):
        response = self.client.get('/api/it/feedback/options.json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['activities'][0]['label'], self.activity.label_it)
        self.assertEqual(data['categories'][0]['label'], self.cat.label_it)
        self.assertEqual(data['magnitudeProblems'][0]['label'], self.pb_magnitude.label_it)

    def test_display_dates(self):
        date_time_1 = datetime.strptime("24/03/21 20:51", '%d/%m/%y %H:%M')
        date_time_2 = datetime.strptime("28/03/21 5:51", '%d/%m/%y %H:%M')
        r = feedback_factories.ReportFactory(created_in_suricate=date_time_1, last_updated_in_suricate=date_time_2)
        self.assertEqual("03/24/2021 8:51 p.m.", r.created_in_suricate_display)
        self.assertEqual("03/28/2021 5:51 a.m.", r.last_updated_in_suricate_display)
