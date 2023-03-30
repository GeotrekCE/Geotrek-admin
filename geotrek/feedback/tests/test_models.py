import json
import uuid
from datetime import timedelta
from hashlib import md5
from unittest import mock

from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.contrib.gis.geos import Point
from django.core import management
from django.test.testcases import TestCase
from django.test.utils import override_settings
from django.utils import timezone, translation
from freezegun.api import freeze_time
from mapentity.tests.factories import SuperUserFactory, UserFactory

from geotrek import __version__
from geotrek.authent.tests.factories import UserProfileFactory
from geotrek.feedback.admin import (PredefinedEmailAdmin,
                                    WorkflowDistrictAdmin,
                                    WorkflowManagerAdmin)
from geotrek.feedback.helpers import SuricateMessenger
from geotrek.feedback.models import (PendingSuricateAPIRequest,
                                     PredefinedEmail, Report, SelectableUser,
                                     TimerEvent, WorkflowDistrict,
                                     WorkflowManager)
from geotrek.feedback.tests.factories import (ReportFactory,
                                              ReportStatusFactory,
                                              WorkflowDistrictFactory,
                                              WorkflowManagerFactory)
from geotrek.feedback.tests.test_suricate_sync import (
    SURICATE_MANAGEMENT_SETTINGS, SuricateTests,
    SuricateWorkflowTests, test_for_report_and_basic_modes,
    test_for_workflow_mode)
from geotrek.zoning.tests.factories import DistrictFactory


SURICATE_WORKFLOW_SETTINGS = {
    "SURICATE_RELOCATED_REPORT_MESSAGE": "Le Signalement ne concerne pas le Département du Gard - Relocalisé hors du Département",
    "SKIP_MANAGER_MODERATION": False
}


class TestFeedbackModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.report = ReportFactory(email="mail@mail.fr", eid=666)

    def test_get_display_name(self):
        translation.activate('en')
        s = f'<a data-pk=\"{self.report.pk}\" href=\"{self.report.get_detail_url()}\" title=\"Report {self.report.pk}\">Report {self.report.pk}</a>'
        self.assertEqual(self.report.name_display, s)

    @override_settings(SURICATE_WORKFLOW_ENABLED=True)
    def test_get_display_name_suricate(self):
        translation.activate('en')
        s = f'<a data-pk=\"{self.report.pk}\" href=\"{self.report.get_detail_url()}\" title=\"Report {self.report.eid}\">Report {self.report.eid}</a>'
        self.assertEqual(self.report.name_display, s)

    @override_settings(ALLOWED_HOSTS=["geotrek.local"])
    def test_get_full_url(self):
        s = f"geotrek.local/report/{self.report.pk}/"
        self.assertEqual(self.report.full_url, s)


@override_settings(SURICATE_MANAGEMENT_SETTINGS=SURICATE_MANAGEMENT_SETTINGS)
@override_settings(SURICATE_WORKFLOW_SETTINGS=SURICATE_WORKFLOW_SETTINGS)
class TestTimerEventClass(SuricateWorkflowTests):

    @classmethod
    def setUpTestData(cls):
        SuricateWorkflowTests.setUpTestData()
        cls.programmed_report = ReportFactory(status=cls.programmed_status, uses_timers=True, assigned_user=UserFactory(password="drowssap"))
        cls.waiting_report = ReportFactory(status=cls.waiting_status, uses_timers=True, assigned_user=UserFactory(password="drowssap"))
        cls.waiting_report_no_timers = ReportFactory(status=cls.waiting_status, uses_timers=False, assigned_user=UserFactory(password="drowssap"))
        cls.event1 = TimerEvent.objects.create(step=cls.waiting_status, report=cls.waiting_report)
        cls.event2 = TimerEvent.objects.create(step=cls.programmed_status, report=cls.programmed_report)
        # Event 3 simulates report that was waiting and is now programmed
        cls.event3 = TimerEvent.objects.create(step=cls.waiting_status, report=cls.programmed_report)

    def test_notification_dates_waiting(self):
        event = TimerEvent.objects.create(step=self.waiting_status, report=self.waiting_report)
        self.assertEqual(event.date_event.date(), timezone.now().date())
        self.assertEquals(event.deadline, event.date_event + timedelta(days=6))

    def test_notification_dates_programmed(self):
        event = TimerEvent.objects.create(step=self.programmed_status, report=self.programmed_report)
        self.assertEqual(event.date_event.date(), timezone.now().date())
        self.assertEquals(event.deadline, event.date_event + timedelta(days=7))

    def test_no_timers_when_disabled_on_reports(self):
        TimerEvent.objects.create(step=self.waiting_status, report=self.waiting_report_no_timers)
        self.assertEqual(TimerEvent.objects.filter(report=self.waiting_report_no_timers.pk).count(), 0)

    @test_for_workflow_mode
    @freeze_time("2099-07-04")
    def test_events_notify(self):
        # Assert before notification
        self.assertFalse(self.event1.notification_sent)
        self.assertEqual(self.waiting_report.status, self.waiting_status)
        # Notify
        self.event1.notify_if_needed()
        self.assertTrue(self.event1.notification_sent)
        # Assert report status changed to late
        self.assertEqual(self.waiting_report.status, self.late_intervention_status)

    @freeze_time("2099-07-04")
    def test_command_clears_obsolete_events(self):
        self.assertFalse(self.event2.is_obsolete())
        self.assertEqual(TimerEvent.objects.count(), 3)
        management.call_command("check_timers")
        # Event2 deleted as well as the others because running the command makes it obsolete
        self.assertEqual(TimerEvent.objects.count(), 0)


class MockRequest:
    pass


@override_settings(SURICATE_MANAGEMENT_SETTINGS=SURICATE_MANAGEMENT_SETTINGS)
@override_settings(SURICATE_WORKFLOW_SETTINGS=SURICATE_WORKFLOW_SETTINGS)
class TestWorkflowUserModels(TestCase):

    def test_strings(self):
        user = UserProfileFactory(user__username="Chloe", user__email="chloe.price@notmail.com").user
        self.assertIn(user, SelectableUser.objects.all())
        as_selectable = SelectableUser.objects.get(username="Chloe")
        self.assertEqual(str(as_selectable), "Chloe (chloe.price@notmail.com)")
        manager = WorkflowManager.objects.create(user=user)
        self.assertEqual(str(manager), "Chloe (chloe.price@notmail.com)")

    @test_for_workflow_mode
    def test_can_create_several_managers(self):
        ma = WorkflowManagerAdmin(WorkflowManager, AdminSite())
        request = MockRequest()
        request.user = SuperUserFactory()
        # We can create a manager when there is none
        self.assertIs(ma.has_add_permission(request), True)
        user = UserProfileFactory(user__username="Chloe", user__email="chloe.price@notmail.com").user
        WorkflowManager.objects.create(user=user)
        # We cannot create a manager if there is one
        self.assertIs(ma.has_add_permission(request), False)

    @test_for_workflow_mode
    def test_can_create_several_workflow_districts(self):
        admin = WorkflowDistrictAdmin(WorkflowDistrict, AdminSite())
        request = MockRequest()
        request.user = SuperUserFactory()
        # We can create a district when there is none
        self.assertIs(admin.has_add_permission(request), True)
        district = DistrictFactory(name="The place to be")
        WorkflowDistrict.objects.create(district=district)
        # We cannot create a district if there is one
        self.assertIs(admin.has_add_permission(request), False)
        self.assertEqual(str(WorkflowDistrict.objects.first()), 'The place to be')

    @test_for_workflow_mode
    def test_can_create_predefined_emails(self):
        admin = PredefinedEmailAdmin(PredefinedEmail, AdminSite())
        request = MockRequest()
        request.user = SuperUserFactory()
        # We can create emails
        self.assertIs(admin.has_add_permission(request), True)

    @test_for_workflow_mode
    def test_cannot_create_several_managers(self):
        ma = WorkflowManagerAdmin(WorkflowManager, AdminSite())
        request = MockRequest()
        request.user = SuperUserFactory()
        # We can create a manager when there is none
        self.assertIs(ma.has_add_permission(request), True)
        # We cannot create a manager when there is one
        WorkflowManagerFactory(user=UserFactory())
        self.assertIs(ma.has_add_permission(request), False)

    @test_for_workflow_mode
    def test_cannot_create_several_workflow_districts(self):
        admin = WorkflowDistrictAdmin(WorkflowDistrict, AdminSite())
        request = MockRequest()
        request.user = SuperUserFactory()
        # We cannot create a district
        self.assertIs(admin.has_add_permission(request), True)
        WorkflowDistrictFactory(district=DistrictFactory())
        self.assertIs(admin.has_add_permission(request), False)

    @test_for_report_and_basic_modes
    def test_cannot_create_predefined_emails(self):
        admin = PredefinedEmailAdmin(PredefinedEmail, AdminSite())
        request = MockRequest()
        request.user = SuperUserFactory()
        # We cannot create emails
        self.assertIs(admin.has_add_permission(request), False)


class TestReportColor(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.status = ReportStatusFactory(identifier='filed', label="Classé sans suite", color="#888888")
        cls.report = ReportFactory(status=cls.status)
        cls.report_1 = ReportFactory(status=None)

    @override_settings(ENABLE_REPORT_COLORS_PER_STATUS=True)
    def test_status_color(self):
        self.assertEqual(self.report.color, "#888888")

    @override_settings(ENABLE_REPORT_COLORS_PER_STATUS=True)
    def test_default_color(self):
        self.assertEqual(self.report_1.color, "#ffff00")

    @override_settings(ENABLE_REPORT_COLORS_PER_STATUS=False)
    def test_disabled_color(self):
        self.assertEqual(self.report.color, "#ffff00")

    @override_settings(ENABLE_REPORT_COLORS_PER_STATUS=True)
    @override_settings(MAPENTITY_CONFIG={})
    def test_no_default_color(self):
        self.assertEqual(self.report_1.color, "#ffff00")


class TestPendingAPIRequests(SuricateTests):

    @classmethod
    def setUpTestData(cls):
        cls.status = ReportStatusFactory(identifier='filed', label="En cours", color="#888888")
        cls.status_waiting = ReportStatusFactory(identifier='waiting', label="En cours", color="#888888")
        super().setUpTestData()

    @override_settings(SURICATE_WORKFLOW_ENABLED=True)
    @mock.patch("geotrek.feedback.helpers.requests.get")
    def test_failed_get_on_management_api(self, mocked):
        uid = uuid.uuid4()
        report = ReportFactory.create(email='john.doe@nowhere.com',
                                      comment="This is a 'comment'",
                                      assigned_user=self.user,
                                      external_uuid=uid)
        # Report lock fails the first time
        self.build_timeout_request_patch(mocked)
        self.assertRaises(Exception, report.lock_in_suricate())
        self.assertEquals(PendingSuricateAPIRequest.objects.count(), 1)
        pending_lock_report = PendingSuricateAPIRequest.objects.first()
        self.assertEquals(pending_lock_report.request_type, "GET")
        self.assertEquals(pending_lock_report.api, "MAN")
        self.assertEquals(pending_lock_report.endpoint, "wsLockAlert")
        self.assertEquals(pending_lock_report.params, json.dumps({"uid_alerte": str(report.formatted_external_uuid)}))
        self.assertEquals(pending_lock_report.retries, 0)
        self.assertEquals(pending_lock_report.error_message, "('Failed to access Suricate API - Status code: 408',)")
        # Report lock fails a second time
        management.call_command('retry_failed_requests_and_mails')
        self.assertEquals(PendingSuricateAPIRequest.objects.count(), 1)
        pending_lock_report.refresh_from_db()
        self.assertEquals(pending_lock_report.retries, 1)
        self.assertEquals(pending_lock_report.error_message, "('Failed to access Suricate API - Status code: 408',)")
        # Lock succeeds at second retry
        self.build_get_request_patch(mocked)
        management.call_command('retry_failed_requests_and_mails')
        self.assertEquals(PendingSuricateAPIRequest.objects.count(), 0)

    @override_settings(SURICATE_WORKFLOW_ENABLED=True)
    @mock.patch("geotrek.feedback.helpers.requests.post")
    def test_failed_post_on_standard_api(self, mocked):
        # Report sent fails the first time
        self.build_timeout_request_patch(mocked)
        self.assertRaises(
            Exception,
            ReportFactory.create(
                email='john.doe@nowhere.com',
                comment="This is a 'comment'",
                assigned_user=self.user
            )
        )
        self.assertEquals(PendingSuricateAPIRequest.objects.count(), 1)
        pending_post_report = PendingSuricateAPIRequest.objects.first()
        self.assertEquals(pending_post_report.request_type, "POST")
        self.assertEquals(pending_post_report.api, "STA")
        self.assertEquals(pending_post_report.endpoint, "wsSendReport")
        check = md5(
            (SuricateMessenger().standard_manager.PRIVATE_KEY_CLIENT_SERVER + 'john.doe@nowhere.com').encode()
        ).hexdigest()
        # Point used in ReportFactory
        long, lat = Point(700000, 6600000, srid=settings.SRID).transform(4326, clone=True).coords
        params = json.dumps({
            'id_origin': 'geotrek',
            'id_user': 'john.doe@nowhere.com',
            'lat': lat,
            'long': long,
            'report': "This is a 'comment'",
            'activite': None,
            'nature_prb': None,
            'ampleur_prb': None,
            'check': check,
            'os': 'linux',
            'version': f"{__version__}"
        })
        self.assertEquals(pending_post_report.params, params)
        self.assertEquals(pending_post_report.retries, 0)
        self.assertEquals(pending_post_report.error_message, "('Failed to access Suricate API - Status code: 408',)")
        # Report sent fails a second time
        management.call_command('retry_failed_requests_and_mails')
        self.assertEquals(PendingSuricateAPIRequest.objects.count(), 1)
        pending_post_report.refresh_from_db()
        self.assertEquals(pending_post_report.retries, 1)
        # Report sent succeeds at second retry
        self.build_post_request_patch(mocked)
        management.call_command('retry_failed_requests_and_mails')
        self.assertEquals(PendingSuricateAPIRequest.objects.count(), 0)

    @override_settings(SURICATE_WORKFLOW_ENABLED=True)
    @mock.patch("geotrek.feedback.helpers.requests.post")
    def test_failed_post_on_management_api(self, mocked):
        # Create a report with an UID - emulates report from Suricate
        uid = uuid.uuid4()
        geom = Point(700000, 6600000, srid=settings.SRID)
        report = Report.objects.create(external_uuid=uid, status=self.status, geom=geom, email="john.doe@nowhere.com")
        # Report update fails the first time
        self.build_timeout_request_patch(mocked)
        messenger = SuricateMessenger(PendingSuricateAPIRequest)
        self.assertRaises(
            Exception,
            messenger.update_status(uid, self.status_waiting.identifier, "a nice and polite message", "a brief message")
        )
        self.assertEquals(PendingSuricateAPIRequest.objects.count(), 1)
        report.refresh_from_db()
        self.assertEquals(1, report.sync_errors)
        pending_post = PendingSuricateAPIRequest.objects.first()
        self.assertEquals(pending_post.request_type, "POST")
        self.assertEquals(pending_post.api, "MAN")
        self.assertEquals(pending_post.endpoint, "wsUpdateStatus")
        check = md5(
            (messenger.gestion_manager.PRIVATE_KEY_CLIENT_SERVER + messenger.gestion_manager.ID_ORIGIN + str(uid)).encode()
        ).hexdigest()
        # Point used in ReportFactory
        params = json.dumps({
            "id_origin": "geotrek",
            "statut": "waiting",
            "txt_changestatut": "a brief message",
            "txt_changestatut_sentinelle": "a nice and polite message",
            "check": check,
            "uid_alerte": str(uid)
        })
        self.assertEquals(pending_post.params, params)
        self.assertEquals(pending_post.retries, 0)
        self.assertEquals(pending_post.error_message, "('Failed to access Suricate API - Status code: 408',)")
        # Report sent fails a second time
        management.call_command('retry_failed_requests_and_mails')
        self.assertEquals(PendingSuricateAPIRequest.objects.count(), 1)
        pending_post.refresh_from_db()
        self.assertEquals(pending_post.retries, 1)
        self.assertEquals(1, report.sync_errors)
        # Report sent succeeds at second retry
        self.build_post_request_patch(mocked)
        management.call_command('retry_failed_requests_and_mails')
        self.assertEquals(PendingSuricateAPIRequest.objects.count(), 0)
        report.refresh_from_db()
        self.assertEquals(0, report.sync_errors)
        # Special case
        # "waiting" status from suricate API does not override internal statuses on sync_suricate
        # therefore, we need to manually set report status to waiting here if this is the call that failed
        self.assertEqual('waiting', report.status.identifier)
