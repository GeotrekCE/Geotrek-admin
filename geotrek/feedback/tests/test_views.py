import csv
import json
import os
from datetime import datetime
from io import StringIO
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Permission
from django.core import mail
from django.core.cache import caches
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import translation
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from freezegun import freeze_time
from mapentity.tests.factories import SuperUserFactory, UserFactory
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from geotrek.authent.tests.base import AuthentFixturesMixin
from geotrek.common.tests import (CommonTest, GeotrekAPITestCase,
                                  TranslationResetMixin)
from geotrek.common.utils.testdata import (get_dummy_uploaded_document,
                                           get_dummy_uploaded_image,
                                           get_dummy_uploaded_image_svg)
from geotrek.feedback import models as feedback_models
from geotrek.maintenance.tests.factories import (
    InfrastructureInterventionFactory, ReportInterventionFactory)

from . import factories as feedback_factories
from .test_suricate_sync import (SURICATE_REPORT_SETTINGS,
                                 test_for_all_suricate_modes,
                                 test_for_management_mode,
                                 test_for_report_and_basic_modes,
                                 test_for_workflow_mode)


class ReportViewsetMailSend(TestCase):
    @override_settings(SURICATE_REPORT_SETTINGS=SURICATE_REPORT_SETTINGS)
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
                'email': 'test_post@geotrek.local',
                'comment': 'Test comment <>',
                'activity': feedback_factories.ReportActivityFactory.create().pk,
                'problem_magnitude': feedback_factories.ReportProblemMagnitudeFactory.create().pk,
            })
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, "Geotrek : Signal a mistake")
        self.assertIn("We acknowledge receipt of your feedback", mail.outbox[1].body)
        self.assertEqual(mail.outbox[1].from_email, settings.DEFAULT_FROM_EMAIL)
        created_report = feedback_models.Report.objects.filter(email="test_post@geotrek.local").first()
        self.assertEqual(created_report.comment, "Test comment &lt;&gt;")


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

    @test_for_workflow_mode
    def test_report_layer_cache(self):
        """
        This test checks report's cache
        """
        cache = caches[settings.MAPENTITY_CONFIG['GEOJSON_LAYERS_CACHE_BACKEND']]

        # There are 5 queries to get layer
        with self.assertNumQueries(4):
            response = self.client.get(reverse("feedback:report-drf-list",
                                               format="geojson"))
        self.assertEqual(len(response.json()['features']), 4)

        # We check the content was created and cached
        last_update_status = feedback_models.Report.latest_updated()
        geojson_lookup = f"fr_report_{last_update_status.isoformat()}_{self.user.pk}_geojson_layer"
        cache_content = cache.get(geojson_lookup)

        self.assertEqual(response.content, cache_content.content)

        # We have 1 less query because the generation of report was cached
        with self.assertNumQueries(3):
            self.client.get(reverse("feedback:report-drf-list",
                                    format="geojson"))

        self.classified_report_4 = feedback_factories.ReportFactory(status=self.classified_status)
        # Bypass workflow's save method does not actually save
        self.classified_report_4.save_no_suricate()

        # Cache is updated when we add a report
        with self.assertNumQueries(4):
            self.client.get(reverse("feedback:report-drf-list",
                                    format="geojson"))

        self.filed_report = feedback_factories.ReportFactory(status=self.filed_status)


class ReportViewsTest(GeotrekAPITestCase, CommonTest):
    model = feedback_models.Report
    modelfactory = feedback_factories.ReportFactory
    userfactory = SuperUserFactory
    expected_json_geom = {
        'type': 'Point',
        'coordinates': [3.0, 46.5],
    }
    extra_column_list = ['comment', 'advice']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        feedback_factories.WorkflowManagerFactory(user=UserFactory())

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name
        }

    def get_expected_json_attrs(self):
        return {
            'activity': self.obj.activity.pk,
            'category': self.obj.category.pk,
            'comment': self.obj.comment,
            'related_trek': None,
            'email': self.obj.email,
            'status': self.obj.status_id,
            'problem_magnitude': self.obj.problem_magnitude.pk
        }

    def get_expected_datatables_attrs(self):
        return {
            'activity': self.obj.activity.label,
            'category': self.obj.category.label,
            'date_update': '17/03/2020 00:00:00',
            'id': self.obj.pk,
            'status': str(self.obj.status),
            'eid': f'<a data-pk="{self.obj.pk}" href="/report/{self.obj.pk}/" title="Report {self.obj.pk}">Report {self.obj.pk}</a>'
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
        response = self.client.post(self._get_add_url(), data)
        self.assertEqual(response.status_code, 302)
        obj = self.model.objects.last()
        self.assertEqual(obj.email, data['email'])
        self.logout()

    def test_crud_status(self):
        if self.model is None:
            return  # Abstract test should not run

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

    @test_for_all_suricate_modes
    def test_custom_columns_mixin_on_list(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={'feedback_view': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}List')().columns,
                             ['id', 'eid', 'activity', 'comment', 'advice'])

    @test_for_all_suricate_modes
    def test_custom_columns_mixin_on_export(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={'feedback_export': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}FormatList')().columns,
                             ['id', 'email', 'comment', 'advice'])

    @freeze_time("2020-03-17")
    def test_api_datatables_list_for_model_in_suricate_mode(self):
        self.report = feedback_factories.ReportFactory()
        with override_settings(SURICATE_WORKFLOW_ENABLED=True):
            list_url = '/api/{modelname}/drf/{modelname}s.datatables'.format(modelname=self.model._meta.model_name)
            response = self.client.get(list_url)
            self.assertEqual(response.status_code, 200, f"{list_url} not found")
            content_json = response.json()
            datatable_attrs = {
                'activity': self.report.activity.label,
                'category': self.report.category.label,
                'date_update': '17/03/2020 00:00:00',
                'id': self.report.pk,
                'status': str(self.report.status),
                'eid': f'<a data-pk="{self.report.pk}" href="/report/{self.report.pk}/" title="Report {self.report.eid}">Report {self.report.eid}</a>'
            }
            self.assertEqual(content_json, {'data': [datatable_attrs],
                                            'draw': 1,
                                            'recordsFiltered': 1,
                                            'recordsTotal': 1})


class BaseAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(password='booh')
        perm = Permission.objects.get_by_natural_key('add_report', 'feedback', 'report')
        cls.user.user_permissions.add(perm)

        cls.login_url = '/login/'


class CreateReportsAPITest(BaseAPITest):
    @classmethod
    def setUpTestData(cls):
        cls.add_url = '/api/en/reports/report'
        cls.data = {
            'geom': '{"type": "Point", "coordinates": [3, 46.5]}',
            'email': 'yeah@you.com',
            'activity': feedback_factories.ReportActivityFactory.create().pk,
            'problem_magnitude': feedback_factories.ReportProblemMagnitudeFactory.create().pk
        }

    def post_report_data(self, data):
        client = APIClient()
        response = client.post(self.add_url, data=data,
                               allow_redirects=False)
        self.assertEqual(response.status_code, 201, self.add_url)
        return response

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
        self.data['image'] = get_dummy_uploaded_image()
        self.post_report_data(self.data)
        self.assertTrue(feedback_models.Report.objects.filter(email='yeah@you.com').exists())
        report = feedback_models.Report.objects.get()
        self.assertEqual(report.attachments.count(), 1)
        name, ext = os.path.splitext(report.attachments.first().attachment_file.name)
        self.assertIn("dummy_img", name)
        self.assertIn(".jpeg", ext)
        self.assertTrue(report.attachments.first().is_image)

    @mock.patch('geotrek.feedback.views.logger')
    def test_reports_with_failed_image(self, mock_logger):
        self.data['image'] = get_dummy_uploaded_image_svg()
        self.data['comment'] = "We have a problem"
        new_report_id = self.post_report_data(self.data).data.get('id')
        self.assertTrue(feedback_models.Report.objects.filter(email='yeah@you.com').exists())
        report = feedback_models.Report.objects.get(pk=new_report_id)
        self.assertEqual(report.comment, "We have a problem")
        mock_logger.error.assert_called_with(f"Failed to convert attachment dummy_img.svg for report {new_report_id}: cannot identify image file <InMemoryUploadedFile: dummy_img.svg (image/svg+xml)>")
        self.assertEqual(report.attachments.count(), 0)

    @mock.patch('geotrek.feedback.views.logger')
    def test_reports_with_bad_file_format(self, mock_logger):
        self.data['image'] = get_dummy_uploaded_document()
        self.data['comment'] = "We have a problem"
        new_report_id = self.post_report_data(self.data).data.get('id')
        self.assertTrue(feedback_models.Report.objects.filter(email='yeah@you.com').exists())
        report = feedback_models.Report.objects.get(pk=new_report_id)
        self.assertEqual(report.comment, "We have a problem")
        mock_logger.error.assert_called_with(f"Invalid attachment dummy_file.odt for report {new_report_id} : {{\'attachment_file\': ['File mime type “text/plain” is not allowed for “odt”.']}}")
        self.assertEqual(report.attachments.count(), 0)


class ListCategoriesTest(TranslationResetMixin, BaseAPITest):
    @classmethod
    def setUpTestData(cls):
        cls.cat = feedback_factories.ReportCategoryFactory(label_it='Obstaculo')

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
    @classmethod
    def setUpTestData(cls):
        cls.activity = feedback_factories.ReportActivityFactory(label_it='Hiking')
        cls.cat = feedback_factories.ReportCategoryFactory(label_it='Obstaculo')
        cls.pb_magnitude = feedback_factories.ReportProblemMagnitudeFactory(label_it='Possible')

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


class SuricateViewPermissions(AuthentFixturesMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.workflow_manager_user = UserFactory()
        cls.normal_user = UserFactory()
        cls.super_user = SuperUserFactory()
        cls.classified_status = feedback_factories.ReportStatusFactory(identifier="classified")
        feedback_factories.WorkflowManagerFactory(user=cls.workflow_manager_user)
        cls.admin = SuperUserFactory(username="Admin", password="drowssap")
        cls.report = feedback_factories.ReportFactory(assigned_user=cls.normal_user, status=cls.classified_status)
        cls.report = feedback_factories.ReportFactory(assigned_user=cls.workflow_manager_user, status=cls.classified_status)
        cls.report = feedback_factories.ReportFactory(status=cls.classified_status)
        permission = Permission.objects.get(name__contains='Can read Report')
        permission_export = Permission.objects.get(name__contains='Can export Report')
        cls.workflow_manager_user.user_permissions.add(permission)
        cls.workflow_manager_user.user_permissions.add(permission_export)
        cls.normal_user.user_permissions.add(permission)
        cls.normal_user.user_permissions.add(permission_export)
        cls.intervention = ReportInterventionFactory()
        cls.unrelated_intervention = InfrastructureInterventionFactory()

    @test_for_workflow_mode
    def test_manager_sees_everything(self):
        self.client.force_login(user=self.workflow_manager_user)
        response = self.client.get(reverse('feedback:report_list'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['object_list'].count(), 4)
        response = self.client.get(reverse("feedback:report-drf-list",
                                           format="geojson"),
                                   data={"status": self.classified_status.pk})
        self.assertEqual(len(response.json()['features']), 3)

    @test_for_workflow_mode
    def test_normal_user_sees_only_assigned_reports(self):
        self.client.force_login(user=self.normal_user)
        response = self.client.get(reverse('feedback:report_list'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['object_list'].count(), 1)
        response = self.client.get(reverse("feedback:report-drf-list",
                                           format="geojson"),
                                   data={"status": self.classified_status.pk})
        self.assertEqual(len(response.json()['features']), 1)

    @test_for_workflow_mode
    def test_super_user_sees_everything(self):
        self.client.force_login(user=self.super_user)
        response = self.client.get(reverse('feedback:report_list'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['object_list'].count(), 4)
        response = self.client.get(reverse("feedback:report-drf-list",
                                           format="geojson"),
                                   data={"status": self.classified_status.pk})
        self.assertEqual(len(response.json()['features']), 3)

    @test_for_report_and_basic_modes
    def test_normal_user_sees_everything_1(self):
        self.client.force_login(user=self.normal_user)
        response = self.client.get(reverse('feedback:report_list'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['object_list'].count(), 4)
        response = self.client.get(reverse("feedback:report-drf-list",
                                           format="geojson"),
                                   data={"status": self.classified_status.pk})
        self.assertEqual(len(response.json()['features']), 3, response.json()['features'])

    @test_for_workflow_mode
    def test_cannot_delete_report_intervention(self):
        self.client.force_login(user=self.admin)
        response = self.client.get(f"/intervention/edit/{self.intervention.pk}/", follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertIn("disabled delete", response.content.decode("utf-8"))

    @test_for_workflow_mode
    def test_can_delete_closed_report_intervention(self):
        self.client.force_login(user=self.admin)
        report = self.intervention.target
        report.status = feedback_factories.ReportStatusFactory(identifier='solved')
        report.save()
        response = self.client.get(f"/intervention/edit/{self.intervention.pk}/", follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertIn("delete", response.content.decode("utf-8"))
        self.assertNotIn("disabled delete", response.content.decode("utf-8"))

    @test_for_report_and_basic_modes
    @test_for_management_mode
    def test_can_delete_report_intervention(self):
        self.client.force_login(user=self.admin)
        response = self.client.get(f"/intervention/edit/{self.intervention.pk}/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("delete", response.content.decode("utf-8"))
        self.assertNotIn("disabled delete", response.content.decode("utf-8"))

    @test_for_all_suricate_modes
    def test_can_delete_intervention(self):
        self.client.force_login(user=self.admin)
        response = self.client.get(f"/intervention/edit/{self.unrelated_intervention.pk}/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("delete", response.content.decode("utf-8"))
        self.assertNotIn("disabled delete", response.content.decode("utf-8"))

    @test_for_management_mode
    def test_normal_user_sees_everything_2(self):
        self.client.force_login(user=self.normal_user)
        response = self.client.get(reverse('feedback:report_list'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['object_list'].count(), 4)
        response = self.client.get(reverse("feedback:report-drf-list",
                                           format="geojson"),
                                   data={"status": self.classified_status.pk})
        self.assertEqual(len(response.json()['features']), 3)

    @test_for_workflow_mode
    def test_csv_superuser_sees_emails(self):
        '''Test CSV job costs export does contain emails for superuser'''
        translation.activate('fr')
        self.client.force_login(user=self.super_user)
        response = self.client.get('/report/list/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        reader = csv.DictReader(StringIO(response.content.decode("utf-8")), delimiter=',')
        dict_from_csv = dict(list(reader)[0])
        column_names = list(dict_from_csv.keys())
        self.assertIn("Courriel", column_names)

    @test_for_workflow_mode
    def test_csv_hidden_emails(self):
        '''Test CSV job costs export do not contain emails for supervisor'''
        translation.activate('fr')
        self.client.force_login(user=self.normal_user)
        response = self.client.get('/report/list/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        reader = csv.DictReader(StringIO(response.content.decode("utf-8")), delimiter=',')
        dict_from_csv = dict(list(reader)[0])
        column_names = list(dict_from_csv.keys())
        self.assertNotIn("Courriel", column_names)

    @test_for_workflow_mode
    def test_csv_manager_sees_emails(self):
        '''Test CSV job costs export does contain emails for manager'''
        translation.activate('fr')
        self.client.force_login(user=self.workflow_manager_user)
        response = self.client.get('/report/list/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        reader = csv.DictReader(StringIO(response.content.decode("utf-8")), delimiter=',')
        dict_from_csv = dict(list(reader)[0])
        column_names = list(dict_from_csv.keys())
        self.assertIn("Courriel", column_names)

    @test_for_report_and_basic_modes
    def test_normal_csv_emails(self):
        '''Test CSV job costs export do not contain emails for supervisor'''
        translation.activate('fr')
        self.client.force_login(user=self.normal_user)
        response = self.client.get('/report/list/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        reader = csv.DictReader(StringIO(response.content.decode("utf-8")), delimiter=',')
        dict_from_csv = dict(list(reader)[0])
        column_names = list(dict_from_csv.keys())
        self.assertIn("Courriel", column_names)
