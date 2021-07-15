from geotrek.maintenance.models import InterventionJob
from django.test import TestCase
from geotrek.maintenance.factories import InterventionJobFactory, ManDayFactory, InterventionFactory
from geotrek.maintenance.forms import ManDayFormSet


class ManDayFormTest(TestCase):
    def setUp(self):
        self.interv = InterventionFactory()
        InterventionJob.objects.all().delete()  # Delete extra job created by intervention factory
        self.job1 = InterventionJobFactory(job="Worker", cost=12, active=False)
        self.job2 = InterventionJobFactory(job="Streamer", cost=60, active=True)
        self.job3 = InterventionJobFactory(job="Baker", cost=62, active=True)
        self.manday = ManDayFactory(nb_days=3, job=self.job1, intervention=self.interv)  # Intervention with a deactivated job

    def test_active_jobs_only_display(self):
        form = ManDayFormSet().forms[0]
        qs = form.fields['job'].queryset  # Create manday form
        self.assertNotIn(self.job1, qs)  # Deactivated does not show
        self.assertIn(self.job2, qs)
        self.assertIn(self.job3, qs)

    def test_inactive_jobs_display_on_edit(self):
        forms = ManDayFormSet(instance=self.interv).forms
        qs1 = forms[0].fields['job'].queryset  # Update manday form
        self.assertIn(self.job1, qs1)  # Deactivated does show
        self.assertIn(self.job3, qs1)
        self.assertIn(self.job3, qs1)
        qs2 = forms[1].fields['job'].queryset  # Create manday form
        self.assertNotIn(self.job1, qs2)  # Deactivated does not show
        self.assertIn(self.job3, qs2)
        self.assertIn(self.job3, qs2)
