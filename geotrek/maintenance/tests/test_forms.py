from unittest import skipIf

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings

from geotrek.authent.tests.factories import UserFactory
from geotrek.core.tests.factories import PathFactory, TopologyFactory
from geotrek.feedback.models import Report, TimerEvent
from geotrek.feedback.tests.factories import (
    ReportFactory,
    ReportStatusFactory,
    WorkflowManagerFactory,
)
from geotrek.maintenance.forms import InterventionForm, ManDayForm, ProjectForm
from geotrek.maintenance.tests.factories import (
    InterventionJobFactory,
    InterventionStatusFactory,
    LightInterventionFactory,
    ManDayFactory,
)
from geotrek.signage.tests.factories import SignageFactory


class ManDayFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.interv = LightInterventionFactory()
        cls.job1 = InterventionJobFactory(job="Worker", cost=12, active=False)
        cls.job2 = InterventionJobFactory(job="Streamer", cost=60, active=True)
        cls.job3 = InterventionJobFactory(job="Baker", cost=62, active=True)
        cls.manday = ManDayFactory(
            nb_days=3, job=cls.job1, intervention=cls.interv
        )  # Intervention with a deactivated job

    def test_active_jobs_only_display_on_create(self):
        form = ManDayForm()
        qs = form.fields["job"].queryset  # Create manday form
        self.assertNotIn(self.job1, qs)  # Deactivated does not show
        self.assertIn(self.job2, qs)
        self.assertIn(self.job3, qs)

    def test_inactive_jobs_display_on_edit(self):
        form = ManDayForm(instance=self.manday)
        qs = form.fields["job"].queryset  # Update manday form
        self.assertIn(self.job1, qs)  # Deactivated does show
        self.assertIn(self.job3, qs)
        self.assertIn(self.job3, qs)

    def test_form_active_job_is_valid(self):
        form = ManDayForm(data={"nb_days": 4, "job": self.job2.pk})
        self.assertTrue(form.is_valid())

    def test_form_inactive_job_is_invalid(self):
        form = ManDayForm(data={"nb_days": 4, "job": self.job1.pk})
        self.assertFalse(form.is_valid())


class InterventionFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        WorkflowManagerFactory(user=cls.user)

        cls.interv = LightInterventionFactory()
        topo = TopologyFactory()
        path = PathFactory()
        cls.topology = f'[{{"pk": {topo.pk}, "paths": [{path.pk}], "positions": {{"0": [0.674882030756843, 0.110030805790642]}}}}]'

        cls.interv_status_10 = InterventionStatusFactory(order=10)
        cls.interv_status_20 = InterventionStatusFactory(order=20)
        cls.interv_status_30 = InterventionStatusFactory(order=30)

        cls.waiting_status = ReportStatusFactory(identifier="waiting", timer_days="10")
        cls.programmed_status = ReportStatusFactory(
            identifier="programmed", timer_days="10"
        )
        cls.solved_status = ReportStatusFactory(identifier="solved_intervention")

        cls.target_signage = (SignageFactory(),)
        cls.target_report = ReportFactory.create(
            status=cls.waiting_status, uses_timers=True
        )

    def create_intervention_form(self, status, target=None, is_report=False):
        target = target
        kwargs = {
            "data": {
                "name": "abc",
                "topology": self.topology,
                "target": target,
                "begin_date": "10/02/2024",
                "status": status,
            },
            "user": self.user,
        }
        if is_report:
            kwargs["target_type"] = ContentType.objects.get_for_model(
                self.target_report
            ).pk
            kwargs["target_id"] = self.target_report.pk
        return InterventionForm(**kwargs)

    def update_intervention_form(self, status, intervention):
        kwargs = {
            "instance": intervention,
            "data": {
                "name": "abc",
                "begin_date": "10/02/2024",
                "end_date": "10/09/2024",
                "status": status,
            },
            "user": self.user,
        }
        return InterventionForm(**kwargs)

    def _assert_report_status_and_timers(self, expected_status, expected_timer_count):
        report = Report.objects.first()
        self.assertEqual(report.status.identifier, expected_status)
        timers = TimerEvent.objects.all()
        self.assertEqual(timers.count(), expected_timer_count)
        if expected_timer_count:
            self.assertEqual(timers[0].step.identifier, expected_status)

    def test_end_date_after_start_date(self):
        form = InterventionForm(
            instance=self.interv,
            user=self.user,
            data={"begin_date": "10/02/2024", "end_date": "09/02/2024"},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Begin date is after end date", str(form.errors))

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    @override_settings(SURICATE_WORKFLOW_ENABLED=True)
    def test_create_intervention_if_target_is_not_report(self):
        form = self.create_intervention_form(
            status=self.interv_status_30, target=self.target_signage
        )
        self.assertTrue(form.is_valid())

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    @override_settings(SURICATE_WORKFLOW_ENABLED=True)
    def test_create_intervention_with_10_or_20_status_for_report(self):
        test_cases = [
            self.interv_status_10,
            self.interv_status_20,
        ]

        for status in test_cases:
            with self.subTest(status=status.order):
                # report reset
                report = Report.objects.first()
                report.status = self.waiting_status
                report.save()

                # TimerEvent reset
                TimerEvent.objects.all().delete()

                form = self.create_intervention_form(
                    status=status, target=self.target_report, is_report=True
                )
                self.assertTrue(form.is_valid())

                form.save()
                self._assert_report_status_and_timers("programmed", 1)

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    @override_settings(SURICATE_WORKFLOW_ENABLED=True)
    def test_create_intervention_with_30_status_for_report(self):
        # report reset
        report = Report.objects.first()
        report.status = self.waiting_status
        report.save()

        form = self.create_intervention_form(
            status=self.interv_status_30, target=self.target_report, is_report=True
        )
        self.assertTrue(form.is_valid())

        form.save()
        self._assert_report_status_and_timers("solved_intervention", 0)

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    @override_settings(SURICATE_WORKFLOW_ENABLED=True)
    def test_update_intervention_to_30_status_for_report(self):
        # report reset
        report = Report.objects.first()
        report.status = self.waiting_status
        report.save()

        intervention = LightInterventionFactory(
            status=self.interv_status_20, target=self.target_report
        )

        form = self.update_intervention_form(
            status=self.interv_status_30, intervention=intervention
        )
        self.assertTrue(form.is_valid())

        form.save()
        self._assert_report_status_and_timers("solved_intervention", 0)

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    @override_settings(SURICATE_WORKFLOW_ENABLED=True)
    def test_update_intervention_from_10_to_20_status_for_report(self):
        """
        check if the status of the linked report change from "waiting" to "programmed" when the status of the intervention change between status 10 and 20. Moreover, the timer should be start only once.
        """
        # report reset
        report = Report.objects.first()
        report.status = self.waiting_status
        report.save()

        intervention = LightInterventionFactory(
            status=self.interv_status_10, target=self.target_report
        )

        form = self.update_intervention_form(
            status=self.interv_status_20, intervention=intervention
        )
        self.assertTrue(form.is_valid())

        form.save()
        self._assert_report_status_and_timers("programmed", 1)

        form = self.update_intervention_form(
            status=self.interv_status_10, intervention=intervention
        )
        self.assertTrue(form.is_valid())

        form.save()
        self._assert_report_status_and_timers("programmed", 1)


class ProjectDateFormTest(TestCase):
    def test_begin_end_date(self):
        user = UserFactory()
        form = ProjectForm(
            user=user,
            data={
                "name": "project",
                "begin_year": 2022,
                "end_year": 2021,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Start year is after end year", str(form.errors))
