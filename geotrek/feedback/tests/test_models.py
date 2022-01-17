from datetime import timedelta
from geotrek.feedback.admin import WorkflowManagerAdmin
from geotrek.authent.tests.factories import UserProfileFactory
from django.contrib.admin.sites import AdminSite

from django.core import management
from django.test.testcases import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from freezegun.api import freeze_time
from mapentity.tests.factories import UserFactory, SuperUserFactory

from geotrek.feedback.models import SelectableUser, TimerEvent, WorkflowManager
from geotrek.feedback.tests.factories import ReportFactory, ReportStatusFactory
from geotrek.feedback.tests.test_suricate_sync import SuricateWorkflowTests


class TestFeedbackModel(TestCase):
    def setUp(self):
        self.report = ReportFactory(email="mail@mail.fr")

    def test_get_display_name(self):
        s = f'<a data-pk=\"{self.report.pk}\" href=\"{self.report.get_detail_url()}\" title="mail@mail.fr">mail@mail.fr</a>'
        self.assertEqual(self.report.name_display, s)

    @override_settings(ALLOWED_HOSTS=["geotrek.local"])
    def test_get_full_url(self):
        s = f"geotrek.local/report/{self.report.pk}/"
        self.assertEqual(self.report.full_url, s)


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


class TestWorkflowUserModels(TestCase):

    def test_strings(self):
        user = UserProfileFactory(user__username="Chloe", user__email="chloe.price@notmail.com").user
        self.assertIn(user, SelectableUser.objects.all())
        as_selectable = SelectableUser.objects.get(username="Chloe")
        self.assertEqual(str(as_selectable), "Chloe (chloe.price@notmail.com)")
        manager = WorkflowManager.objects.create(user=user)
        self.assertEqual(str(manager), "Chloe (chloe.price@notmail.com)")

    def test_cannot_create_several_managers(self):
        ma = WorkflowManagerAdmin(WorkflowManager, AdminSite())
        request = MockRequest()
        request.user = SuperUserFactory()
        # We can create a manager when there is none
        self.assertIs(ma.has_add_permission(request), True)
        user = UserProfileFactory(user__username="Chloe", user__email="chloe.price@notmail.com").user
        WorkflowManager.objects.create(user=user)
        # We cannot create a manager if there is one
        self.assertIs(ma.has_add_permission(request), False)


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
