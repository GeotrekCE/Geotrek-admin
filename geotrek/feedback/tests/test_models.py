from datetime import timedelta

from django.core import management
from django.test.testcases import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from freezegun.api import freeze_time
from mapentity.tests.factories import UserFactory

from geotrek.feedback.models import TimerEvent
from geotrek.feedback.tests.factories import ReportFactory
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

    def setUp(cls):
        super().setUp()
        cls.programmed_report = ReportFactory(status=cls.programmed_status, assigned_user=UserFactory(password="drowssap"))
        cls.waiting_report = ReportFactory(status=cls.waiting_status, assigned_user=UserFactory(password="drowssap"))
        cls.event1 = TimerEvent.objects.create(step=cls.waiting_status, report=cls.waiting_report)
        cls.event2 = TimerEvent.objects.create(step=cls.programmed_status, report=cls.programmed_report)
        # Event 3 simulates report that was waiting and is now programmed
        cls.event3 = TimerEvent.objects.create(step=cls.waiting_status, report=cls.programmed_report)

    def test_notification_dates_waiting(self):
        event = TimerEvent.objects.create(step=self.waiting_status, report=self.waiting_report)
        self.assertEqual(event.date_event.date(), timezone.now().date())
        self.assertEquals(event.date_notification, event.date_event + timedelta(days=6))

    def test_notification_dates_programmed(self):
        event = TimerEvent.objects.create(step=self.programmed_status, report=self.programmed_report)
        self.assertEqual(event.date_event.date(), timezone.now().date())
        self.assertEquals(event.date_notification, event.date_event + timedelta(days=7))

    @freeze_time("2099-07-04")
    def test_events_notify(self):
        # Assert before notification
        self.assertFalse(self.event1.notification_sent)
        self.assertEqual(self.waiting_report.status, self.waiting_status)
        # Notify
        self.event1.notify_if_needed()
        self.assertTrue(self.event1.notification_sent)
        # Assert report status changed to late
        self.assertEqual(self.waiting_report.status, self.intervention_late_status)

    @freeze_time("2099-07-04")
    def test_command_clears_obsolete_events(self):
        self.assertFalse(self.event2.is_obsolete())
        self.assertEqual(TimerEvent.objects.count(), 3)
        management.call_command("check_timers")
        # Event2 deleted as well as the others because running the command makes it obsolete
        self.assertEqual(TimerEvent.objects.count(), 0)
