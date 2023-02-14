import uuid
from datetime import datetime
from hashlib import md5
from unittest import mock

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core import mail
from django.forms.widgets import CheckboxInput, EmailInput, HiddenInput, Select
from django.urls.base import reverse
from django.utils import translation
from mapentity.tests.factories import SuperUserFactory, UserFactory
from mapentity.widgets import MapWidget
from tinymce.widgets import TinyMCE

from geotrek.authent.tests.factories import UserProfileFactory
from geotrek.feedback.forms import ReportForm
from geotrek.feedback.helpers import SuricateMessenger
from geotrek.feedback.models import (TimerEvent, WorkflowDistrict,
                                     WorkflowManager)
from geotrek.feedback.tests.factories import (PredefinedEmailFactory,
                                              ReportFactory,
                                              ReportStatusFactory)
from geotrek.feedback.tests.test_suricate_sync import (
    SuricateWorkflowTests, test_for_report_and_basic_modes,
    test_for_workflow_mode)
from geotrek.maintenance.forms import InterventionForm
from geotrek.maintenance.models import InterventionStatus
from geotrek.maintenance.tests.factories import (InterventionFactory,
                                                 ReportInterventionFactory)
from geotrek.zoning.tests.factories import DistrictFactory


class TestSuricateForms(SuricateWorkflowTests):
    fixtures = ['geotrek/maintenance/fixtures/basic.json']

    @classmethod
    def setUpTestData(cls):
        SuricateWorkflowTests.setUpTestData()
        cls.filed_report = ReportFactory(status=cls.filed_status, external_uuid=uuid.uuid4(), assigned_user=UserFactory())
        cls.filed_report_1 = ReportFactory(status=cls.filed_status, external_uuid=uuid.uuid4())
        cls.filed_report_2 = ReportFactory(status=cls.filed_status, external_uuid=uuid.uuid4())
        cls.waiting_report = ReportFactory(status=cls.waiting_status, uses_timers=True, external_uuid=uuid.uuid4())
        cls.intervention = ReportInterventionFactory(date=datetime(year=1997, month=4, day=4).date())
        cls.waiting_report = ReportFactory(status=cls.waiting_status, uses_timers=True, external_uuid=uuid.uuid4())
        cls.solved_intervention_report = ReportFactory(status=cls.solved_intervention_status, external_uuid=uuid.uuid4())
        cls.predefined_email_1 = PredefinedEmailFactory()
        cls.predefined_email_2 = PredefinedEmailFactory()
        cls.status_no_timer = ReportStatusFactory(identifier='notimer', label="No timer", timer_days=0)
        cls.status_timer_6 = ReportStatusFactory(identifier='timer6', label="Timer 6", timer_days=6)
        cls.status_timer_3 = ReportStatusFactory(identifier='timer3', label="Timer 3", timer_days=3)
        cls.other_user = UserFactory()
        UserProfileFactory.create(user=cls.other_user, extended_username="Communauté des Communes des Communautés Communataires")
        cls.district = DistrictFactory(geom='SRID=2154;MULTIPOLYGON(((-1 -1, -1 1, 1 1, 1 -1, -1 -1)))')
        WorkflowDistrict.objects.create(district=cls.district)

    def setUp(self):
        self.client.login(username="Admiin", password="drowssap")

    @test_for_report_and_basic_modes
    def test_creation_form_common(self):
        data = {
            'email': 'test@test.fr',
            'geom': Point(700000, 6600000, srid=settings.SRID)
        }
        form = ReportForm(data)
        keys = form.fields.keys()
        self.assertIsInstance(form.fields["geom"].widget, MapWidget)
        self.assertIsInstance(form.fields["email"].widget, EmailInput)
        self.assertIsInstance(form.fields["comment"].widget, TinyMCE)
        self.assertIsInstance(form.fields["activity"].widget, Select)
        self.assertIsInstance(form.fields["category"].widget, Select)
        self.assertIsInstance(form.fields["status"].widget, Select)
        self.assertIsInstance(form.fields["problem_magnitude"].widget, Select)
        self.assertIsInstance(form.fields["related_trek"].widget, Select)
        self.assertNotIn('message_sentinel', keys)
        self.assertNotIn('message_administrators', keys)
        self.assertNotIn('message_sentinel_predefined', keys)
        self.assertNotIn('message_supervisor', keys)
        self.assertIsInstance(form.fields["assigned_user"].widget, Select)
        self.assertIsInstance(form.fields["uses_timers"].widget, CheckboxInput)
        self.assertFalse(form.errors)

    @test_for_report_and_basic_modes
    def test_update_form_common(self):
        form = ReportForm(instance=self.filed_report)
        keys = form.fields.keys()
        self.assertIsInstance(form.fields["geom"].widget, MapWidget)
        self.assertIsInstance(form.fields["email"].widget, EmailInput)
        self.assertIsInstance(form.fields["comment"].widget, TinyMCE)
        self.assertIsInstance(form.fields["activity"].widget, Select)
        self.assertIsInstance(form.fields["category"].widget, Select)
        self.assertIsInstance(form.fields["status"].widget, Select)  # Remove this in report mode
        self.assertIsInstance(form.fields["problem_magnitude"].widget, Select)
        self.assertIsInstance(form.fields["related_trek"].widget, Select)
        self.assertNotIn('message_sentinel', keys)
        self.assertNotIn('message_administrators', keys)
        self.assertNotIn('message_sentinel_predefined', keys)
        self.assertNotIn('message_supervisor', keys)
        self.assertIsInstance(form.fields["assigned_user"].widget, Select)
        self.assertIsInstance(form.fields["uses_timers"].widget, CheckboxInput)
        self.assertFalse(form.errors)  # assert form is valid

    @test_for_workflow_mode
    def test_creation_form_specifics_2(self):
        data = {
            'email': 'test@test.fr',
            'geom': Point(700000, 6600000, srid=settings.SRID)
        }
        form = ReportForm(data)
        keys = form.fields.keys()

        self.assertIsInstance(form.fields["geom"].widget, MapWidget)
        self.assertIsInstance(form.fields["email"].widget, EmailInput)
        self.assertIsInstance(form.fields["comment"].widget, TinyMCE)
        self.assertIsInstance(form.fields["activity"].widget, Select)
        self.assertIsInstance(form.fields["category"].widget, Select)
        self.assertIsInstance(form.fields["status"].widget, HiddenInput)
        self.assertIsInstance(form.fields["problem_magnitude"].widget, Select)
        self.assertIsInstance(form.fields["related_trek"].widget, Select)
        self.assertNotIn('message_sentinel', keys)
        self.assertNotIn('message_administrators', keys)
        self.assertNotIn('message_sentinel_predefined', keys)
        self.assertNotIn('message_supervisor', keys)
        self.assertIsInstance(form.fields["assigned_user"].widget, HiddenInput)
        self.assertIsInstance(form.fields["uses_timers"].widget, HiddenInput)

    @test_for_workflow_mode
    def test_update_form_specifics_2(self):
        form = ReportForm(instance=self.filed_report)
        keys = form.fields.keys()
        self.assertIsInstance(form.fields["geom"].widget, MapWidget)
        self.assertIsInstance(form.fields["email"].widget, HiddenInput)
        self.assertIsInstance(form.fields["comment"].widget, HiddenInput)
        self.assertIsInstance(form.fields["activity"].widget, HiddenInput)
        self.assertIsInstance(form.fields["category"].widget, HiddenInput)
        self.assertIsInstance(form.fields["status"].widget, Select)
        self.assertIsInstance(form.fields["problem_magnitude"].widget, HiddenInput)
        self.assertIsInstance(form.fields["related_trek"].widget, Select)
        self.assertIn('message_sentinel', keys)
        self.assertIn('message_administrators', keys)
        self.assertIn('message_sentinel_predefined', keys)
        self.assertIn('message_supervisor', keys)
        self.assertIsInstance(form.fields["assigned_user"].widget, Select)
        self.assertIsInstance(form.fields["uses_timers"].widget, CheckboxInput)

    @test_for_workflow_mode
    @mock.patch("geotrek.feedback.helpers.requests.get")
    @mock.patch("geotrek.feedback.helpers.requests.post")
    def test_workflow_assign_step(self, mocked_post, mocked_get):
        translation.activate('fr')
        self.build_get_request_patch(mocked_get)
        self.build_post_request_patch(mocked_post)
        mails_before = len(mail.outbox)
        # When assigning a user to a report
        data = {
            'assigned_user': str(self.other_user.pk),
            'email': 'test@test.fr',
            'geom': self.filed_report.geom,
            'message_sentinel': "Your message",
            "uses_timers": True
        }
        form = ReportForm(instance=self.filed_report, data=data)
        form.save()
        # Assert report status changes
        self.assertEquals(self.filed_report.status.identifier, "waiting")
        # Asser timer is created
        self.assertEquals(TimerEvent.objects.filter(report=self.filed_report, step=self.waiting_status).count(), 1)
        # Assert data forwarded to Suricate
        check = md5(
            (SuricateMessenger().gestion_manager.PRIVATE_KEY_CLIENT_SERVER + SuricateMessenger().gestion_manager.ID_ORIGIN + str(self.filed_report.formatted_external_uuid)).encode()
        ).hexdigest()
        call1 = mock.call(
            'http://suricate.wsmanagement.example.com/wsSendMessageSentinelle',
            {'id_origin': 'geotrek', 'uid_alerte': self.filed_report.formatted_external_uuid, 'message': 'Your message', 'check': check},
            auth=('', '')
        )
        call2 = mock.call(
            'http://suricate.wsmanagement.example.com/wsUpdateStatus',
            {'id_origin': 'geotrek', 'uid_alerte': self.filed_report.formatted_external_uuid, 'statut': 'waiting', 'txt_changestatut': 'Your message', 'txt_changestatut_sentinelle': 'Your message', 'check': check},
            auth=('', '')
        )
        mocked_post.assert_has_calls([call1, call2], any_order=True)
        mocked_get.assert_called_once_with(
            f"http://suricate.wsmanagement.example.com/wsLockAlert?uid_alerte={self.filed_report.formatted_external_uuid}&id_origin=geotrek&check={check}",
            auth=('', '')
        )
        # Assert user is notified
        self.assertEqual(len(mail.outbox), mails_before + 1)
        self.assertEqual(mail.outbox[-1].subject, "[Geotrek] Nouveau Signalement à traiter")
        self.assertEqual(mail.outbox[-1].to, [self.filed_report.assigned_user.email])

    @test_for_workflow_mode
    def test_workflow_program_step(self):
        # When creating an intervention for a report
        user = SuperUserFactory(username="admin", password="dadadad")
        data = {
            'name': "test_interv",
            'date': "2025-12-12",
            'status': 2,
            'structure': user.profile.structure.pk,
        }
        form = InterventionForm(user=user, target_type=self.waiting_report.get_content_type_id(), target_id=self.waiting_report.pk, data=data)
        form.is_valid()
        form.save()
        # Assert timer is created
        self.assertEquals(TimerEvent.objects.filter(report=self.waiting_report).count(), 1)
        # Assert report status changed
        self.waiting_report.refresh_from_db()
        self.assertEquals(self.waiting_report.status.identifier, "programmed")

    @test_for_workflow_mode
    @mock.patch("geotrek.feedback.helpers.requests.post")
    def test_solving_report_intervention(self, mocked_post):
        translation.activate('fr')
        mails_before = len(mail.outbox)
        self.build_post_request_patch(mocked_post)
        # Report has a linked intervention
        interv = InterventionFactory(
            status=InterventionStatus.objects.get(status="planifiée"),
            target=self.interv_report
        )
        # Trigger resolving intervention
        user = SuperUserFactory(username="admin", password="dadadad")
        data = {
            'name': interv.name,
            'date': interv.date,
            'status': 3,    # pk for "Terminée" from fixtures
            'structure': user.profile.structure.pk
        }
        form = InterventionForm(user=user, instance=interv, data=data)
        form.is_valid()
        form.save()
        # Assert report changes status and manager is notified
        self.assertEqual(self.interv_report.status.identifier, "solved_intervention")
        self.assertEqual(self.interv_report.assigned_user, WorkflowManager.objects.first().user)
        self.assertEqual(len(mail.outbox), mails_before + 1)
        self.assertEqual(mail.outbox[-1].subject, "[Geotrek] Un Signalement est à clôturer")
        self.assertEqual(mail.outbox[-1].to, [self.workflow_manager.user.email])

    @test_for_report_and_basic_modes
    def test_can_create_intervention(self):
        response = self.client.get(reverse('feedback:report_detail', kwargs={'pk': self.filed_report.pk}), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertIn("Ajouter une intervention", response.content.decode("utf-8"))

    @test_for_workflow_mode
    def test_can_only_create_intervention_once_1(self):
        response = self.client.get(reverse('feedback:report_detail', kwargs={'pk': self.filed_report.pk}), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertNotIn("Ajouter une intervention", response.content.decode("utf-8"))

    @test_for_workflow_mode
    def test_predefined_emails_serialized(self):
        response = self.client.get(reverse('feedback:report_add'), follow=True)
        emails_data = "{\"1\": {\"label\": \"Predefined Email 0\", \"text\": \"Some email body content 0\"}, \"2\": {\"label\": \"Predefined Email 1\", \"text\": \"Some email body content 1\"}"
        self.assertEquals(response.status_code, 200)
        self.assertIn(emails_data, response.content.decode("utf-8"))

    @test_for_workflow_mode
    def test_date_intervention_serialized(self):
        report = self.intervention.target
        report.assigned_user = self.admin
        report.save()
        response = self.client.get(f"/report/edit/{self.intervention.target.pk}/")
        emails_data = ""
        self.assertEquals(response.status_code, 200)
        self.assertIn(emails_data, response.content.decode("utf-8"))

    @test_for_workflow_mode
    def test_can_only_create_intervention_once_2(self):
        response = self.client.get(reverse('feedback:report_detail', kwargs={'pk': self.waiting_report.pk}), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertIn("Ajouter une intervention", response.content.decode("utf-8"))

    @test_for_workflow_mode
    @mock.patch("geotrek.feedback.helpers.requests.get")
    @mock.patch("geotrek.feedback.helpers.requests.post")
    def test_workflow_resolve_step(self, mocked_post, mocked_get):
        self.build_get_request_patch(mocked_get)
        self.build_post_request_patch(mocked_post)
        # When assigning a user to a report
        data = {
            'email': 'test@test.fr',
            'geom': self.solved_intervention_report.geom,
            'status': self.resolved_status.pk,
            'message_sentinel': "Your message",
            'message_administrators': "Your message admins"
        }
        form = ReportForm(instance=self.solved_intervention_report, data=data)
        form.save()
        # Assert report status changes
        self.assertEquals(self.solved_intervention_report.status.identifier, "solved")
        # Assert data forwarded to Suricate
        check = md5(
            (SuricateMessenger().gestion_manager.PRIVATE_KEY_CLIENT_SERVER + SuricateMessenger().gestion_manager.ID_ORIGIN + str(self.solved_intervention_report.formatted_external_uuid)).encode()
        ).hexdigest()
        call1 = mock.call(
            'http://suricate.wsmanagement.example.com/wsSendMessageSentinelle',
            {'id_origin': 'geotrek', 'uid_alerte': self.solved_intervention_report.formatted_external_uuid, 'message': 'Your message', 'check': check},
            auth=('', '')
        )
        call2 = mock.call(
            'http://suricate.wsmanagement.example.com/wsUpdateStatus',
            {'id_origin': 'geotrek', 'uid_alerte': self.solved_intervention_report.formatted_external_uuid, 'statut': 'solved', 'txt_changestatut': 'Your message admins', 'txt_changestatut_sentinelle': 'Your message', 'check': check},
            auth=('', '')
        )
        mocked_post.assert_has_calls([call1, call2], any_order=True)

    @test_for_workflow_mode
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_relocate_report_in_district(self, mocked_get):
        self.build_get_request_patch(mocked_get)
        # Relocate report inside of main district
        new_geom = Point(0, 0, srid=2154)
        data = {
            'email': 'test@test.fr',
            'geom': new_geom
        }
        form = ReportForm(instance=self.filed_report_1, data=data)
        form.save()
        # Assert relocation is forwarded to Suricate
        long, lat = new_geom.transform(4326, clone=True).coords
        long_txt = '{0:.6f}'.format(long)
        lat_txt = '{0:.6f}'.format(lat)
        check = md5(
            (SuricateMessenger().gestion_manager.PRIVATE_KEY_CLIENT_SERVER + SuricateMessenger().gestion_manager.ID_ORIGIN + str(self.filed_report_1.formatted_external_uuid)).encode()
        ).hexdigest()
        mocked_get.assert_called_once_with(
            f"http://suricate.wsmanagement.example.com/wsUpdateGPS?uid_alerte={self.filed_report_1.formatted_external_uuid}&gpslatitude={lat_txt}&gpslongitude={long_txt}&id_origin=geotrek&check={check}",
            auth=('', '')
        )

    @test_for_workflow_mode
    @mock.patch("geotrek.feedback.helpers.requests.get")
    @mock.patch("geotrek.feedback.helpers.requests.post")
    def test_relocate_report_outside_district(self, mocked_post, mocked_get):
        self.build_get_request_patch(mocked_get)
        # Relocate report outside of main district
        new_geom = Point(2, 2, srid=2154)
        data = {
            'email': 'test@test.fr',
            'geom': new_geom
        }
        form = ReportForm(instance=self.filed_report_1, data=data)
        form.save()
        # Assert relocation is forwarded to Suricate
        long, lat = new_geom.transform(4326, clone=True).coords
        long_txt = '{0:.6f}'.format(long)
        lat_txt = '{0:.6f}'.format(lat)
        check = md5(
            (SuricateMessenger().gestion_manager.PRIVATE_KEY_CLIENT_SERVER + SuricateMessenger().gestion_manager.ID_ORIGIN + str(self.filed_report_1.formatted_external_uuid)).encode()
        ).hexdigest()
        mocked_post.assert_called_once_with(
            'http://suricate.wsmanagement.example.com/wsUpdateStatus',
            {'id_origin': 'geotrek', 'uid_alerte': self.filed_report_1.formatted_external_uuid, 'statut': 'waiting', 'txt_changestatut': 'Le Signalement ne concerne pas le Département - Relocalisé hors du Département', 'txt_changestatut_sentinelle': 'Le Signalement ne concerne pas le Département - Relocalisé hors du Département', 'check': check},
            auth=('', '')
        )
        mocked_get.assert_called_once_with(
            f"http://suricate.wsmanagement.example.com/wsUpdateGPS?uid_alerte={self.filed_report_1.formatted_external_uuid}&gpslatitude={lat_txt}&gpslongitude={long_txt}&force_update=1&id_origin=geotrek&check={check}",
            auth=('', '')
        )
        self.assertEqual(self.filed_report_1.status, self.rejected_status)

    @test_for_workflow_mode
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_reject_alert_unlocks_in_suricate_when_workflow_enabled(self, mocked_get):
        form = ReportForm(
            instance=self.filed_report_2,
            data={
                'geom': self.filed_report_2.geom,
                'email': self.filed_report_2.email,
                'status': self.rejected_status.pk
            }
        )
        self.assertTrue(form.is_valid)
        form.save()
        check = md5(
            (SuricateMessenger().gestion_manager.PRIVATE_KEY_CLIENT_SERVER + SuricateMessenger().gestion_manager.ID_ORIGIN + str(self.filed_report_2.formatted_external_uuid)).encode()
        ).hexdigest()
        mocked_get.assert_called_once_with(
            f"http://suricate.wsmanagement.example.com/wsUnlockAlert?uid_alerte={self.filed_report_2.formatted_external_uuid}&id_origin=geotrek&check={check}",
            auth=('', '')
        )
        self.filed_report_2.refresh_from_db()
        self.assertEqual(self.filed_report_2.status, self.rejected_status)

    @test_for_report_and_basic_modes
    @mock.patch("geotrek.feedback.helpers.requests.post")
    def test_timer_creation(self, mocked_post):
        # Relocate report inside of main district
        new_geom = Point(0, 0, srid=2154)
        data = {
            'commment': "We have important news",
            'status': self.status_timer_3.pk,
            'email': 'test@test.fr',
            'geom': new_geom,
            'uses_timers': True
        }
        # Test Timer is created when report is created
        form = ReportForm(data=data)
        report = form.save()
        self.assertEqual(TimerEvent.objects.count(), 1)
        self.assertEqual(TimerEvent.objects.first().step.identifier, "timer3")
        data = {
            'commment': "We have important news",
            'status': self.status_timer_6.pk,
            'email': 'test@test.fr',
            'geom': new_geom,
            'uses_timers': True
        }
        form = ReportForm(instance=report, data=data)
        form.save()
        # Test Timers are updated when report is updated
        self.assertEqual(TimerEvent.objects.count(), 2)
        for timer in TimerEvent.objects.all():
            if timer.is_obsolete():
                timer.delete()
        self.assertEqual(TimerEvent.objects.count(), 1)
        self.assertEqual(TimerEvent.objects.first().step.identifier, "timer6")
        # Test Timer is removed if unecessary
        data = {
            'commment': "We have important news",
            'status': self.status_no_timer.pk,
            'email': 'test@test.fr',
            'geom': new_geom,
            'uses_timers': True
        }
        form = ReportForm(instance=report, data=data)
        form.save()
        self.assertEqual(TimerEvent.objects.count(), 1)
        for timer in TimerEvent.objects.all():
            if timer.is_obsolete():
                timer.delete()
        self.assertEqual(TimerEvent.objects.count(), 0)
