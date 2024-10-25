from unittest import skipIf

from django.conf import settings
from django.test import TestCase, override_settings
from geotrek.authent.tests.factories import UserFactory
from geotrek.maintenance.tests.factories import InterventionJobFactory, LightInterventionFactory, ManDayFactory, InterventionStatusFactory
from geotrek.signage.tests.factories import SignageFactory
from geotrek.core.tests.factories import TopologyFactory, PathFactory
from geotrek.maintenance.forms import InterventionForm, ManDayForm, ProjectForm


class ManDayFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.interv = LightInterventionFactory()
        cls.job1 = InterventionJobFactory(job="Worker", cost=12, active=False)
        cls.job2 = InterventionJobFactory(job="Streamer", cost=60, active=True)
        cls.job3 = InterventionJobFactory(job="Baker", cost=62, active=True)
        cls.manday = ManDayFactory(nb_days=3, job=cls.job1, intervention=cls.interv)  # Intervention with a deactivated job

    def test_active_jobs_only_display_on_create(self):
        form = ManDayForm()
        qs = form.fields['job'].queryset  # Create manday form
        self.assertNotIn(self.job1, qs)  # Deactivated does not show
        self.assertIn(self.job2, qs)
        self.assertIn(self.job3, qs)

    def test_inactive_jobs_display_on_edit(self):
        form = ManDayForm(instance=self.manday)
        qs = form.fields['job'].queryset  # Update manday form
        self.assertIn(self.job1, qs)  # Deactivated does show
        self.assertIn(self.job3, qs)
        self.assertIn(self.job3, qs)

    def test_form_active_job_is_valid(self):
        form = ManDayForm(data={
            'nb_days': 4,
            'job': self.job2.pk
        })
        self.assertTrue(form.is_valid())

    def test_form_inactive_job_is_invalid(self):
        form = ManDayForm(data={
            'nb_days': 4,
            'job': self.job1.pk
        })
        self.assertFalse(form.is_valid())


class InterventionFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.interv = LightInterventionFactory()
        cls.user = UserFactory()
        topo = TopologyFactory()
        path = PathFactory()
        cls.topology = '[{"pk": %d, "paths": [%d], "positions": {"0": [0.674882030756843, 0.110030805790642]}}]' % (topo.pk, path.pk)
        cls.target = SignageFactory(),
        cls.interv_status = InterventionStatusFactory(order=30)

    def test_end_date_after_start_date(self):
        form = InterventionForm(
            instance=self.interv,
            user=self.user,
            data={"begin_date": "10/02/2024", "end_date": "09/02/2024"},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Begin date is after end date", str(form.errors))

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    @override_settings(SURICATE_WORKFLOW_ENABLED=True)
    def test_create_intervention_if_target_is_not_report(self):
        form = InterventionForm(
            data={
                "name": "abc",
                "topology": self.topology,
                "target": self.target,
                "begin_date": "10/02/2024",
                "status": self.interv_status
            },
            user=self.user,
        )
        self.assertTrue(form.is_valid())


class ProjectDateFormTest(TestCase):

    def test_begin_end_date(self):
        user = UserFactory()
        form = ProjectForm(
            user=user,
            data={
                'name': 'project',
                'begin_year': 2022,
                'end_year': 2021,
            })
        self.assertFalse(form.is_valid())
        self.assertIn("Start year is after end year", str(form.errors))
