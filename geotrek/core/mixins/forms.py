from copy import deepcopy

from django.conf import settings
from django.contrib.gis.forms import LineStringField
from django.contrib.gis.geos import LineString, fromstr
from django.forms import BooleanField, HiddenInput, ValidationError
from django.utils.translation import gettext_lazy as _

from geotrek.common.forms import CommonForm
from geotrek.core.fields import (
    LineTopologyField,
    PointLineTopoGeomField,
    PointTopoGeomField,
)
from geotrek.core.models import Topology
from geotrek.core.widgets import GeotrekMapWidget


class PointTopologyFormMixin(CommonForm):
    """
    Form mixin for drawing points, on or off the path network depending on whether paths exist.
    """

    geomfields = ["topology"]
    topology = PointTopoGeomField(label="")

    class Meta(CommonForm.Meta):
        fields = [*CommonForm.Meta.fields, "topology"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["topology"].required = False

    def save(self, *args, **kwargs):
        topology = self.cleaned_data.pop("topology")
        instance = super().save(*args, **kwargs)
        if topology is not None:
            instance.mutate(topology)
        return instance


class LineTopologyFormMixin(CommonForm):
    """
    Form mixin for drawing linear topologies on or off the path network, depending on:
      - whether paths exist
      - the user's permissions
    """

    geomfields = ["topology", "geom"]
    topology = LineTopologyField(required=False, label="")
    geom = LineStringField(
        required=False,
        widget=GeotrekMapWidget(
            attrs={
                "target_map": "topology",
                "snapping_config": {
                    "enabled": True,
                    "layers": ["core.Path"],
                    "snap_distance": 20,
                },
            }
        ),
    )
    topology_changed = BooleanField(required=False, widget=HiddenInput())
    geom_changed = BooleanField(required=False, widget=HiddenInput())

    class Meta(CommonForm.Meta):
        fields = [
            *CommonForm.Meta.fields,
            "topology",
            "geom",
            "topology_changed",
            "geom_changed",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add topology_changed and geom_changed to the fields layout
        if self.fieldslayout is not None:
            self.fieldslayout = deepcopy(self.fieldslayout)
            self.fieldslayout.append("geom_changed")
            self.fieldslayout.append("topology_changed")
            self._init_layout()

        if self.instance and self.instance.pk:
            self.fields["topology"].initial = self.instance

        if not self.is_drawing_off_path_network_allowed():
            self.disable_drawing_off_network_at_init()

    def disable_drawing_off_network_at_init(self):
        self.fields["geom"].disabled = True
        self.fields["geom"].widget = GeotrekMapWidget(
            attrs={"target_map": "topology", "modifiable": False}
        )
        self.fields.pop("geom_changed")

    def is_drawing_off_path_network_allowed(self):
        if not settings.PATH_MODEL_ENABLED:
            return True
        return self.user.has_perm("core.can_draw_off_path_network")

    def clean(self):
        data = super().clean()
        self.validate_exclusive_inputs(data)
        self.validate_off_network_permission(data)
        self.validate_creation_requires_input(data)
        self.clear_irrelevant_field_errors(data)
        self.discard_unused_fields(data)
        return data

    def validate_exclusive_inputs(self, data):
        """A geometry can be drawn on the network or off, never both."""
        if data.get("geom_changed") and data.get("topology_changed"):
            raise ValidationError(
                _(
                    "The geometry can only be drawn on or off the path network, not both."
                )
            )

    def validate_off_network_permission(self, data):
        if (
            data.get("geom_changed")
            and isinstance(data.get("geom"), LineString)
            and not self.is_drawing_off_path_network_allowed()
        ):
            raise ValidationError(
                _("You are not allowed to draw off the path network.")
            )

    def validate_creation_requires_input(self, data):
        """At creation, geometry and topology cannot both be left empty."""
        if (
            self.instance.pk is None
            and not data.get("geom_changed")
            and not data.get("topology_changed")
        ):
            raise ValidationError(_("A geometry must be provided."))

    def clear_irrelevant_field_errors(self, data):
        """
        Only one of geom/topology is actually used per submission. Drop validation
        errors on the field that wasn't the one being edited.
        """
        if data.get("topology_changed") and "geom" in self.errors:
            del self.errors["geom"]
            # This geom will be overwritten by triggers
            data["geom"] = fromstr("POINT (0 0)")
        if data.get("geom_changed") and "topology" in self.errors:
            del self.errors["topology"]

    def discard_unused_fields(self, data):
        # Discard geom if it hasn't been marked as changed, otherwise a slight shift caused by
        # transforms will cause the geometry to be modified, and the object to be decoupled
        if not data.get("geom_changed") and data.get("geom") is not None:
            data["geom"] = None

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        if self.cleaned_data.get("topology_changed"):
            topology = self.cleaned_data.pop("topology")
            instance.mutate(topology)
        if not self.cleaned_data.get("geom_changed"):
            instance.geom = self.instance.geom
        return instance


class PointLineTopologyFormMixin(LineTopologyFormMixin):
    """
    Form mixin for drawing line/point topologies on or off the path network, depending on:
      - whether paths exist
      - the user's permissions
    """

    # Parent's topology field handles line topologies. This geom field handles:
    #   - line geometries
    #   - point geometries
    #   - point topologies
    # This allows to use only two widgets: one for line topologies, and one for point/line geometries.
    geom = PointLineTopoGeomField(
        label="",
        required=False,
        target_map="topology",
    )

    def disable_drawing_off_network_at_init(self):
        self.fields["geom"].widget.attrs["allowed_types"] = ["POINT"]

    def clean(self):
        # An equivalent to validate_exclusive_inputs must be executed before reroute_point_topology
        # sets geom_changed to False.
        # We should wait until after reroute_point_topology to raise the corresponding ValidationError
        # and call super().clean(), because in case of a ValidationError, clean()'s return value is
        # discarded and self.cleaned_data is used instead.
        geom_and_topo_changed = self.cleaned_data.get(
            "geom_changed"
        ) and self.cleaned_data.get("topology_changed")
        self.reroute_point_topology(self.cleaned_data)
        if geom_and_topo_changed:
            raise ValidationError(
                _(
                    "The geometry can only be drawn on or off the path network, not both."
                )
            )
        return super().clean()

    def reroute_point_topology(self, data):
        """
        The geom field can also carry a point topology (see PointLineTopoGeomField).
        When that happens, treat it as a topology submission instead of a geometry one.
        """
        geom = data.get("geom")
        if data.get("geom_changed") and isinstance(geom, Topology):
            data["topology"] = geom
            data["topology_changed"] = True
            data["geom"] = None
            data["geom_changed"] = False
