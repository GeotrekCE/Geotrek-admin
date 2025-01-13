import csv
import json
import re
from io import StringIO
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Permission
from django.core import mail
from django.core.cache import caches
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.module_loading import import_string
from freezegun import freeze_time
from mapentity.tests.factories import SuperUserFactory, UserFactory
from rest_framework.reverse import reverse

from geotrek.authent.tests.base import AuthentFixturesMixin
from geotrek.feedback import models as feedback_models
from geotrek.maintenance.tests.factories import (
    InfrastructureInterventionFactory, ReportInterventionFactory)

from ...common.tests import CommonTest
from . import factories as feedback_factories
from .test_suricate_sync import (SURICATE_REPORT_SETTINGS,
                                 test_for_all_suricate_modes,
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
        response = self.client.post(
            '/api/en/reports/report',
            {
                'geom': '{\"type\":\"Point\",\"coordinates\":[4.3728446995373815,43.856935212211454]}',
                'email': 'test_post@geotrek.local',
                'comment': 'Test comment <>',
                'activity': feedback_factories.ReportActivityFactory.create().pk,
                'problem_magnitude': feedback_factories.ReportProblemMagnitudeFactory.create().pk,
            })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(mail.outbox[-1].subject, "Geotrek : Signal a mistake")
        self.assertIn("We acknowledge receipt of your feedback", mail.outbox[-1].body)
        self.assertEqual(mail.outbox[-1].from_email, settings.DEFAULT_FROM_EMAIL)
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
        geojson_lookup = f"en_report_{last_update_status.isoformat()}_{self.user.pk}_geojson_layer"
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


class ReportViewsTest(CommonTest):
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
            'color': self.obj.status.color,
            'name': str(self.obj),
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
        return {'geom': 'FOO'}, 'Invalid geometry value.'

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
        self.assertTrue(re.match(r"/report/[0-9]*/", response.url))
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

    @test_for_workflow_mode
    def test_creation_redirects_to_list_view(self):
        data = {
            'geom': '{"type": "Point", "coordinates": [0, 0]}',
            'email': 'yeah@you.com',
            'activity': feedback_factories.ReportActivityFactory.create().pk,
            'problem_magnitude': feedback_factories.ReportProblemMagnitudeFactory.create().pk,
            'category': feedback_factories.ReportCategoryFactory.create().pk,
            'comment': 'a comment'
        }
        response = self.client.post(self.model.get_add_url(), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url=reverse('feedback:report_list'))


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
        self.assertEqual(response.status_code, 200)
        self.assertIn("disabled delete", response.content.decode("utf-8"))

    @test_for_workflow_mode
    def test_can_delete_closed_report_intervention(self):
        self.client.force_login(user=self.admin)
        report = self.intervention.target
        report.status = feedback_factories.ReportStatusFactory(identifier='solved')
        report.save()
        response = self.client.get(f"/intervention/edit/{self.intervention.pk}/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("delete", response.content.decode("utf-8"))
        self.assertNotIn("disabled delete", response.content.decode("utf-8"))

    @test_for_report_and_basic_modes
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

    @test_for_workflow_mode
    def test_csv_superuser_sees_emails(self):
        '''Test CSV job costs export does contain emails for superuser'''
        self.client.force_login(user=self.super_user)
        response = self.client.get('/report/list/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        reader = csv.DictReader(StringIO(response.content.decode("utf-8")), delimiter=',')
        dict_from_csv = dict(list(reader)[0])
        column_names = list(dict_from_csv.keys())
        self.assertIn("Email", column_names)

    @test_for_workflow_mode
    def test_csv_hidden_emails(self):
        '''Test CSV job costs export do not contain emails for supervisor'''
        self.client.force_login(user=self.normal_user)
        response = self.client.get('/report/list/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        reader = csv.DictReader(StringIO(response.content.decode("utf-8")), delimiter=',')
        dict_from_csv = dict(list(reader)[0])
        column_names = list(dict_from_csv.keys())
        self.assertNotIn("Email", column_names)

    @test_for_workflow_mode
    def test_csv_manager_sees_emails(self):
        '''Test CSV job costs export does contain emails for manager'''
        self.client.force_login(user=self.workflow_manager_user)
        response = self.client.get('/report/list/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        reader = csv.DictReader(StringIO(response.content.decode("utf-8")), delimiter=',')
        dict_from_csv = dict(list(reader)[0])
        column_names = list(dict_from_csv.keys())
        self.assertIn("Email", column_names)

    @test_for_workflow_mode
    def test_filters_manager_sees_emails(self):
        '''Test list FilterSet does contain emails for manager'''
        self.client.force_login(user=self.workflow_manager_user)
        response = self.client.get('/report/filter/')
        self.assertContains(response, '<input type="text" name="email"')

    @test_for_workflow_mode
    def test_filters_hidden_emails(self):
        '''Test list FilterSet do not contain emails for supervisor'''
        self.client.force_login(user=self.normal_user)
        response = self.client.get('/report/filter/')
        self.assertNotContains(response, '<input type="text" name="email"')

    @test_for_report_and_basic_modes
    def test_normal_filters_emails(self):
        '''Test list FilterSet do contain emails for regular user'''
        self.client.force_login(user=self.normal_user)
        response = self.client.get('/report/filter/')
        self.assertContains(response, '<input type="text" name="email"')

    @test_for_report_and_basic_modes
    def test_normal_csv_emails(self):
        '''Test CSV job costs export do contain emails for regular user'''
        self.client.force_login(user=self.normal_user)
        response = self.client.get('/report/list/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        reader = csv.DictReader(StringIO(response.content.decode("utf-8")), delimiter=',')
        dict_from_csv = dict(list(reader)[0])
        column_names = list(dict_from_csv.keys())
        self.assertIn("Email", column_names)
