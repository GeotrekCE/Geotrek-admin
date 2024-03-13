import csv
import json
from io import StringIO
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Permission
from django.core import mail
from django.core.cache import caches
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import translation
from mapentity.tests.factories import SuperUserFactory, UserFactory
from rest_framework.reverse import reverse

from geotrek.authent.tests.base import AuthentFixturesMixin
from geotrek.feedback import models as feedback_models
from geotrek.maintenance.tests.factories import (
    InfrastructureInterventionFactory,
    ReportInterventionFactory,
)

from . import factories as feedback_factories
from .test_suricate_sync import (
    SURICATE_REPORT_SETTINGS,
    test_for_all_suricate_modes,
    test_for_report_and_basic_modes,
    test_for_workflow_mode,
)


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
