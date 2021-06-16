from django.conf import settings
from django.core.checks import Error
from django.test import TestCase

from unittest import skipIf

from django.test.utils import override_settings

from geotrek.core.factories import TrailFactory, PathFactory
from geotrek.authent.factories import UserFactory
from geotrek.core.forms import TrailForm, PathForm


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class TopologyFormTest(TestCase):
    def test_save_form_when_topology_has_not_changed(self):
        user = UserFactory()
        topo = TrailFactory()
        form = TrailForm(instance=topo, user=user)
        self.assertEqual(topo, form.instance)
        form.cleaned_data = {'topology': topo}
        form.save()
        self.assertEqual(topo, form.instance)


class PathFormTest(TestCase):
    def test_overlapping_path(self):
        user = UserFactory()
        PathFactory.create(geom='SRID=4326;LINESTRING(3 45, 3 46)')
        # Just intersecting
        form1 = PathForm(
            user=user,
            data={'geom': '{"geom": "LINESTRING(2.5 45.5, 3.5 45.5)", "snap": [null, null]}'}
        )
        self.assertTrue(form1.is_valid(), str(form1.errors))
        # Overlapping
        form2 = PathForm(
            user=user,
            data={'geom': '{"geom": "LINESTRING(3 45.5, 3 46.5)", "snap": [null, null]}'}
        )
        self.assertFalse(form2.is_valid(), str(form2.errors))

    @override_settings(HIDDEN_FORM_FIELDS={'path': ['structure', 'im_missing']})
    def test_hidden_fields_configuration_check(self):
        errors = PathForm.check_fields_to_hide()
        expected_errors = [
            Error(
                "Cannot hide field 'im_missing'",
                hint='Field not included in form',
                obj='geotrek.core.forms.PathForm'
            )
        ]
        self.assertEqual(errors, expected_errors)
