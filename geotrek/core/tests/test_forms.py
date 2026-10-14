from unittest import mock

from django.contrib.gis.geos import LineString
from django.core.checks import Error
from django.core.exceptions import ValidationError
from django.forms.widgets import HiddenInput
from django.test import TestCase
from django.test.utils import override_settings
from mapentity.tests.factories import SuperUserFactory

from geotrek.authent.tests.factories import UserFactory
from geotrek.core.forms import CertificationTrailFormSet, PathForm, TrailForm
from geotrek.core.mixins.forms import PointLineTopologyFormMixin
from geotrek.core.models import CertificationTrail, Path, Trail
from geotrek.core.tests.factories import (
    CertificationLabelFactory,
    CertificationStatusFactory,
    PathFactory,
    TrailFactory,
)
from geotrek.core.widgets import GeotrekMapWidget


class TopologyFormTest(TestCase):
    def test_save_form_when_topology_has_not_changed(self):
        user = UserFactory()
        topo = TrailFactory()
        form = TrailForm(instance=topo, user=user)
        self.assertEqual(topo, form.instance)
        form.cleaned_data = {"topology": topo}
        form.save()
        self.assertEqual(topo, form.instance)

    def test_geotrek_map_widget_media_for_readonly_geom(self):
        modifiable_widget = GeotrekMapWidget(attrs={"modifiable": True})
        self.assertNotIn(
            "core/mapwidget_disable_edit_readonly_geom.js",
            modifiable_widget.media._js,
        )

        readonly_widget = GeotrekMapWidget(attrs={"modifiable": False})
        self.assertIn(
            "core/mapwidget_disable_edit_readonly_geom.js",
            readonly_widget.media._js,
        )

        point_only_widget = GeotrekMapWidget(attrs={"allowed_types": ["POINT"]})
        self.assertIn(
            "core/mapwidget_disable_edit_readonly_geom.js",
            point_only_widget.media._js,
        )

    def test_line_topology_form_geom_widget_without_permission(self):
        user = UserFactory()
        form = TrailForm(user=user)
        self.assertFalse(form.fields["geom"].widget.modifiable)
        self.assertEqual(
            form.fields["geom"].widget.attrs.get("geom_type"), "LINESTRING"
        )
        self.assertIn(
            "core/mapwidget_disable_edit_readonly_geom.js",
            form.fields["geom"].widget.media._js,
        )

    def test_geotrek_map_widget_media_without_target_map(self):
        widget = GeotrekMapWidget()
        self.assertIn("core/mapwidget_set_geom_changed.js", widget.media._js)
        self.assertIn("core/mapwidget_load_path_layer.js", widget.media._js)

    def test_geotrek_map_widget_media_with_target_map(self):
        widget = GeotrekMapWidget(attrs={"target_map": "topology"})
        self.assertIn("core/mapwidget_set_geom_changed.js", widget.media._js)
        self.assertNotIn("core/mapwidget_load_path_layer.js", widget.media._js)

    def test_clean_removes_geom_error(self):
        user = SuperUserFactory()
        topo = TrailFactory()
        form = TrailForm(
            instance=topo,
            user=user,
            data={
                "name": "t",
                "structure": topo.structure.pk,
                "topology": str(topo.pk),
                "topology_changed": True,
            },
        )
        form.full_clean()
        form._errors["geom"] = form.error_class(["err"])
        form.clean()
        self.assertNotIn("geom", form.errors)

        # Also test geom_changed removes topology errors
        form2 = TrailForm(
            instance=topo,
            user=user,
            data={
                "name": "t",
                "structure": topo.structure.pk,
                "geom": '{"type": "LineString", "coordinates": [[3, 45], [3, 46]]}',
                "geom_changed": True,
            },
        )
        form2.full_clean()
        form2._errors["topology"] = form2.error_class(["err"])
        form2.clean()
        self.assertNotIn("topology", form2.errors)

    def test_exclusive_inputs_raises_validation_error(self):
        user = SuperUserFactory()
        topo = TrailFactory()
        form = TrailForm(
            instance=topo,
            user=user,
            data={
                "name": "t",
                "structure": topo.structure.pk,
                "geom": '{"type": "LineString", "coordinates": [[3, 45], [3, 46]]}',
                "geom_changed": True,
                "topology": str(topo.pk),
                "topology_changed": True,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "The geometry can only be drawn on or off the path network, not both.",
            str(form.errors),
        )

    def test_off_network_permission_raises_validation_error(self):
        user = UserFactory()
        topo = TrailFactory()
        form = TrailForm(instance=topo, user=user)
        cleaned_data = {
            "geom": LineString([(3, 45), (3, 46)]),
            "geom_changed": True,
        }
        with self.assertRaises(ValidationError):
            form.validate_off_network_permission(cleaned_data)

    @override_settings(PATH_MODEL_ENABLED=False)
    def test_is_drawing_off_path_network_allowed_when_path_model_disabled(self):
        user = UserFactory()
        form = TrailForm(user=user)
        self.assertTrue(form.is_drawing_off_path_network_allowed())

    def test_point_line_topology_form_reroute_and_exclusive_inputs(self):
        class DummyPointLineForm(PointLineTopologyFormMixin):
            class Meta(PointLineTopologyFormMixin.Meta):
                model = Trail

        user = SuperUserFactory()
        topo = TrailFactory()
        form = DummyPointLineForm(instance=topo, user=user)
        data = {
            "geom": topo,
            "geom_changed": True,
            "topology_changed": False,
        }
        form.reroute_point_topology(data)
        self.assertEqual(data["topology"], topo)
        self.assertTrue(data["topology_changed"])
        self.assertFalse(data["geom_changed"])

        form.cleaned_data = {
            "geom_changed": True,
            "topology_changed": True,
        }
        with self.assertRaises(ValidationError):
            form.clean()


class PathFormTest(TestCase):
    def test_overlapping_path(self):
        user = UserFactory()
        PathFactory.create(geom="SRID=4326;LINESTRING(3 45, 3 46)")
        # Just intersecting
        form1 = PathForm(
            user=user,
            data={
                "geom": '{"type": "LINESTRING", "coordinates": [[2.5, 45.5], [3.5, 45.5]]}'
            },
        )
        self.assertTrue(form1.is_valid(), str(form1.errors))
        # Overlapping
        form2 = PathForm(
            user=user,
            data={
                "geom": '{"type": "LINESTRING", "coordinates": [[3, 45.5], [3, 46.5]]}'
            },
        )
        self.assertFalse(form2.is_valid(), str(form2.errors))

    @override_settings(HIDDEN_FORM_FIELDS={"path": ["structure", "im_missing"]})
    def test_hidden_fields_configuration_check(self):
        errors = PathForm.check_fields_to_hide()
        expected_errors = [
            Error(
                "Cannot hide field 'im_missing'",
                hint="Field not included in form",
                obj="geotrek.core.forms.PathForm",
            )
        ]
        self.assertEqual(errors, expected_errors)

    @override_settings(HIDDEN_FORM_FIELDS={"path": ["geom", "departure"]})
    def test_hidden_fields_configuration_required_fields(self):
        with self.assertLogs("geotrek.common.forms", level="WARNING") as log:
            user = UserFactory()
            PathForm(user=user)
            self.assertTrue(
                "Ignoring entry in HIDDEN_FORM_FIELDS: field 'geom' is required on form PathForm."
                in log.output[0]
            )

    @override_settings(HIDDEN_FORM_FIELDS={"path": ["name", "departure"]})
    def test_hidden_fields(self):
        user = UserFactory()
        form = PathForm(user=user)
        self.assertIsInstance(form.fields["name"].widget, HiddenInput)
        self.assertIsInstance(form.fields["departure"].widget, HiddenInput)

    def test_invalid_geom_path(self):
        user = UserFactory()
        # Just intersecting
        form1 = PathForm(
            user=user,
            data={"geom": '{"geom": "LINESTRING(2.5 45.5, 2.5 45.5)"}'},
        )
        self.assertFalse(form1.is_valid(), str(form1.errors))

    def test_non_simple_geom_path(self):
        user = UserFactory()
        form = PathForm(
            user=user,
            data={
                "geom": '{"geom": "LINESTRING(0 0, 2 2, 0 2, 2 0)", "snap": [null, null, null, null]}'
            },
        )
        self.assertFalse(form.is_valid())

    def test_clean_geom_none_raises_validation_error(self):
        user = UserFactory()
        form = PathForm(user=user)
        form.cleaned_data = {"geom": None}
        with self.assertRaises(ValidationError):
            form.clean_geom()

    def test_reverse_geom_path_save(self):
        user = UserFactory()
        form = PathForm(
            user=user,
            data={
                "geom": '{"type": "LineString", "coordinates": [[3, 45], [3, 46]]}',
                "reverse_geom": True,
            },
        )
        self.assertTrue(form.is_valid(), str(form.errors))
        path = form.save()
        self.assertIsNotNone(path.pk)

    def test_clean_geom_not_simple(self):
        user = UserFactory()
        form = PathForm(
            user=user,
            data={
                "geom": '{"type": "LineString", "coordinates": [[0, 0], [1, 1], [0, 1], [1, 0]]}',
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Geometry is not simple.", str(form.errors))

    def test_clean_geom_not_valid(self):
        user = UserFactory()
        form = PathForm(user=user)
        geom = mock.MagicMock()
        geom.simple = True
        geom.valid = False
        form.cleaned_data = {"geom": geom}
        with (
            mock.patch.object(Path, "check_path_not_overlap", return_value=True),
            self.assertRaises(ValidationError),
        ):
            form.clean_geom()


class TrailFormTest(TestCase):
    def test_certifications_formset(self):
        trail = TrailFactory.create()
        data = {
            "certifications-TOTAL_FORMS": "2",
            "certifications-INITIAL_FORMS": "0",
            "certifications-MIN_NUM_FORMS": "0",
            "certifications-MAX_NUM_FORMS": "1000",
            "certifications-0-id": "",
            "certifications-0-DELETE": "",
            "certifications-0-certification_label": str(
                CertificationLabelFactory.create().pk
            ),
            "certifications-0-certification_status": str(
                CertificationStatusFactory.create().pk
            ),
            "certifications-1-id": "",
            "certifications-1-DELETE": "",
            "certifications-1-certification_label": str(
                CertificationLabelFactory.create().pk
            ),
            "certifications-1-certification_status": str(
                CertificationStatusFactory.create().pk
            ),
        }
        formset = CertificationTrailFormSet(data, instance=trail)
        self.assertTrue(formset.is_valid())
        formset.save()
        self.assertEqual(CertificationTrail.objects.count(), 2)
