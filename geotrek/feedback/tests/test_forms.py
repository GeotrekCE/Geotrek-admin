from django.forms.widgets import EmailInput, HiddenInput, Select
from mapentity.widgets import MapWidget
from tinymce.widgets import TinyMCE

from geotrek.feedback.forms import ReportForm
from geotrek.feedback.tests.factories import ReportFactory, ReportStatusFactory
from geotrek.feedback.tests.test_suricate_sync import (
    SuricateTests, test_for_management_mode,
    test_for_report_and_basic_modes)


class TestSuricateForms(SuricateTests):
    def setUp(self):
        status = ReportStatusFactory(suricate_id='filed')
        self.report = ReportFactory(status=status)

    @test_for_report_and_basic_modes
    def test_creation_form_common(self):
        data = {
            'email': 'test@test.fr',
            'geom': 'POINT(5.1 6.6)',
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
        self.assertNotIn('message', keys)
        self.assertIsInstance(form.fields["assigned_user"].widget, HiddenInput)
        self.assertFalse(form.errors)

    @test_for_report_and_basic_modes
    def test_update_form_common(self):
        form = ReportForm(instance=self.report)
        keys = form.fields.keys()
        self.assertIsInstance(form.fields["geom"].widget, MapWidget)
        self.assertIsInstance(form.fields["email"].widget, EmailInput)
        self.assertIsInstance(form.fields["comment"].widget, TinyMCE)
        self.assertIsInstance(form.fields["activity"].widget, Select)
        self.assertIsInstance(form.fields["category"].widget, Select)
        self.assertIsInstance(form.fields["status"].widget, Select)
        self.assertIsInstance(form.fields["problem_magnitude"].widget, Select)
        self.assertIsInstance(form.fields["related_trek"].widget, Select)
        self.assertNotIn('message', keys)
        self.assertIsInstance(form.fields["assigned_user"].widget, HiddenInput)
        self.assertFalse(form.errors)  # assert form is valid

    @test_for_management_mode
    def test_creation_form_specifics_2(self):
        data = {
            'email': 'test@test.fr',
            'geom': 'POINT(5.1 6.6)',
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
        self.assertNotIn('message', keys)
        self.assertIsInstance(form.fields["assigned_user"].widget, HiddenInput)

    @test_for_management_mode
    def test_update_form_specifics_2(self):
        form = ReportForm(instance=self.report)
        keys = form.fields.keys()
        self.assertIsInstance(form.fields["geom"].widget, HiddenInput)
        self.assertIsInstance(form.fields["email"].widget, HiddenInput)
        self.assertIsInstance(form.fields["comment"].widget, HiddenInput)
        self.assertIsInstance(form.fields["activity"].widget, HiddenInput)
        self.assertIsInstance(form.fields["category"].widget, HiddenInput)
        self.assertIsInstance(form.fields["status"].widget, Select)
        self.assertIsInstance(form.fields["problem_magnitude"].widget, HiddenInput)
        self.assertIsInstance(form.fields["related_trek"].widget, Select)
        self.assertIn('message', keys)
        self.assertIsInstance(form.fields["assigned_user"].widget, Select)
        # Todo ajouter les contraintes de contenu de status selon old_status / pas de contrainte si autres modes
