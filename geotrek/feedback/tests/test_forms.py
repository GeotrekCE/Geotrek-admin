import uuid
from hashlib import md5
from unittest import mock

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core import mail
from django.forms.widgets import CheckboxInput, EmailInput, HiddenInput, Select
from django.test.utils import override_settings
from django.urls.base import reverse
from django.utils import translation
from mapentity.tests.factories import SuperUserFactory
from mapentity.widgets import MapWidget
from tinymce.widgets import TinyMCE

from geotrek.feedback.forms import ReportForm
from geotrek.feedback.helpers import SuricateMessenger
from geotrek.feedback.models import TimerEvent
from geotrek.feedback.tests.factories import ReportFactory
from geotrek.feedback.tests.test_suricate_sync import (
    SuricateWorkflowTests, test_for_management_mode,
    test_for_report_and_basic_modes)
from geotrek.maintenance.forms import InterventionForm
from geotrek.maintenance.models import InterventionStatus
from geotrek.maintenance.tests.factories import (InterventionFactory,
                                                 InterventionStatusFactory)


class TestSuricateForms(SuricateWorkflowTests):

    @classmethod
    def setUpTestData(cls):
        SuricateWorkflowTests.setUpTestData()
        cls.filed_report = ReportFactory(status=cls.filed_status, uid=uuid.uuid4())
        cls.filed_report_1 = ReportFactory(status=cls.filed_status, uid=uuid.uuid4())
        cls.waiting_report = ReportFactory(status=cls.waiting_status, uses_timers=True, uid=uuid.uuid4())
        cls.solved_intervention_report = ReportFactory(status=cls.solved_intervention_status, uid=uuid.uuid4())

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
        self.assertNotIn('message_supervisor', keys)
        self.assertIsInstance(form.fields["assigned_user"].widget, HiddenInput)
        self.assertIsInstance(form.fields["uses_timers"].widget, HiddenInput)
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
        self.assertIsInstance(form.fields["status"].widget, Select)
        self.assertIsInstance(form.fields["problem_magnitude"].widget, Select)
        self.assertIsInstance(form.fields["related_trek"].widget, Select)
        self.assertNotIn('message_sentinel', keys)
        self.assertNotIn('message_supervisor', keys)
        self.assertIsInstance(form.fields["assigned_user"].widget, HiddenInput)
        self.assertIsInstance(form.fields["uses_timers"].widget, HiddenInput)
        self.assertFalse(form.errors)  # assert form is valid

    @test_for_management_mode
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
        self.assertNotIn('message_supervisor', keys)
        self.assertIsInstance(form.fields["assigned_user"].widget, HiddenInput)
        self.assertIsInstance(form.fields["uses_timers"].widget, HiddenInput)

    @test_for_management_mode
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
        self.assertIn('message_supervisor', keys)
        self.assertIsInstance(form.fields["assigned_user"].widget, Select)
        self.assertIsInstance(form.fields["uses_timers"].widget, CheckboxInput)
        # Todo ajouter les contraintes de contenu de status selon old_status / pas de contrainte si autres modes

    @test_for_management_mode
    @mock.patch("geotrek.feedback.helpers.requests.get")
    @mock.patch("geotrek.feedback.helpers.requests.post")
    def test_workflow_assign_step(self, mocked_post, mocked_get):
        translation.activate('fr')
        self.build_get_request_patch(mocked_get)
        self.build_post_request_patch(mocked_post)
        mails_before = len(mail.outbox)
        # When assigning a user to a report
        data = {
            'assigned_user': str(self.user.pk),
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
            (SuricateMessenger().gestion_manager.PRIVATE_KEY_CLIENT_SERVER + SuricateMessenger().gestion_manager.ID_ORIGIN + str(self.filed_report.uid)).encode()
        ).hexdigest()
        call1 = mock.call(
            'http://suricate.example.com/wsSendMessageSentinelle',
            {'id_origin': 'geotrek', 'uid_alerte': self.filed_report.uid, 'message': 'Your message', 'check': check},
            auth=('', '')
        )
        call2 = mock.call(
            'http://suricate.example.com/wsUpdateStatus',
            {'id_origin': 'geotrek', 'uid_alerte': self.filed_report.uid, 'statut': 'waiting', 'txt_changestatut': 'Your message', 'check': check},
            auth=('', '')
        )
        mocked_post.assert_has_calls([call1, call2], any_order=True)
        mocked_get.assert_called_once_with(
            f"http://suricate.example.com/wsLockAlert?id_origin=geotrek&uid_alerte={self.filed_report.uid}&check={check}",
            auth=('', '')
        )
        # Assert user is notified
        self.assertEqual(len(mail.outbox), mails_before + 1)
        self.assertEqual(mail.outbox[-1].subject, "Geotrek - Nouveau Signalement à traiter")
        self.assertEqual(mail.outbox[-1].to, [self.filed_report.assigned_user.email])

    @test_for_management_mode
    @override_settings()
    def test_workflow_program_step(self):
        # When creating an intervention for a report
        status = InterventionStatusFactory()
        user = SuperUserFactory(username="admin", password="dadadad")
        data = {
            'name': "test_interv",
            'date': "2025-12-12",
            'status': status.pk,
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

    @test_for_management_mode
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
        self.assertEqual(len(mail.outbox), mails_before + 1)
        self.assertEqual(mail.outbox[-1].subject, "Geotrek - Un Signalement est à clôturer")
        self.assertEqual(mail.outbox[-1].to, [self.workflow_manager.user.email])

    @test_for_report_and_basic_modes
    def test_can_create_intervention(self):
        response = self.client.get(reverse('feedback:report_detail', kwargs={'pk': self.filed_report.pk}), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertIn("Ajouter une intervention", response.content.decode("utf-8"))

    @test_for_management_mode
    def test_can_only_create_intervention_once_1(self):
        response = self.client.get(reverse('feedback:report_detail', kwargs={'pk': self.filed_report.pk}), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertNotIn("Ajouter une intervention", response.content.decode("utf-8"))

    @test_for_management_mode
    def test_can_only_create_intervention_once_2(self):
        response = self.client.get(reverse('feedback:report_detail', kwargs={'pk': self.waiting_report.pk}), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertIn("Ajouter une intervention", response.content.decode("utf-8"))

    @test_for_management_mode
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
            'message_sentinel': "Your message"
        }
        form = ReportForm(instance=self.solved_intervention_report, data=data)
        form.save()
        # Assert report status changes
        self.assertEquals(self.solved_intervention_report.status.identifier, "resolved")
        # Assert data forwarded to Suricate
        check = md5(
            (SuricateMessenger().gestion_manager.PRIVATE_KEY_CLIENT_SERVER + SuricateMessenger().gestion_manager.ID_ORIGIN + str(self.solved_intervention_report.uid)).encode()
        ).hexdigest()
        call1 = mock.call(
            'http://suricate.example.com/wsSendMessageSentinelle',
            {'id_origin': 'geotrek', 'uid_alerte': self.solved_intervention_report.uid, 'message': 'Your message', 'check': check},
            auth=('', '')
        )
        call2 = mock.call(
            'http://suricate.example.com/wsUpdateStatus',
            {'id_origin': 'geotrek', 'uid_alerte': self.solved_intervention_report.uid, 'statut': 'resolved', 'txt_changestatut': 'Your message', 'check': check},
            auth=('', '')
        )
        mocked_post.assert_has_calls([call1, call2], any_order=True)
        mocked_get.assert_called_once_with(
            f"http://suricate.example.com/wsUnlockAlert?id_origin=geotrek&uid_alerte={self.solved_intervention_report.uid}&check={check}",
            auth=('', '')
        )

    @test_for_management_mode
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_relocate_report(self, mocked_get):
        self.build_get_request_patch(mocked_get)
        # Relocate report
        new_geom = Point(700000, 6900000, srid=settings.SRID)
        data = {
            'email': 'test@test.fr',
            'geom': new_geom
        }
        form = ReportForm(instance=self.filed_report_1, data=data)
        form.save()
        # Assert relocation is forwarded to Suricate
        long, lat = new_geom.transform(4326, clone=True).coords
        check = md5(
            (SuricateMessenger().gestion_manager.PRIVATE_KEY_CLIENT_SERVER + SuricateMessenger().gestion_manager.ID_ORIGIN + str(self.filed_report_1.uid)).encode()
        ).hexdigest()
        mocked_get.assert_called_once_with(
            f"http://suricate.example.com/wsUpdateGPS?id_origin=geotrek&uid_alerte={self.filed_report_1.uid}&gpslatitude={lat}&gpslongitude={long}&check={check}",
            auth=('', '')
        )
