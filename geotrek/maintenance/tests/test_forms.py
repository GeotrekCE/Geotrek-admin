from django.test import TestCase
from geotrek.maintenance.factories import InterventionJobFactory, LightInterventionFactory, ManDayFactory
from geotrek.maintenance.forms import ManDayForm


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
