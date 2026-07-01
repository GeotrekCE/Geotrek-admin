from copy import deepcopy

from django.conf import settings
from django.contrib.gis.forms import LineStringField
from django.contrib.gis.geos import fromstr, LineString, Point, GEOSGeometry
from django.forms import BooleanField, HiddenInput, ModelForm, ValidationError
from django.utils.translation import gettext_lazy as _
from mapentity.widgets import MapWidget

from geotrek.common.forms import CommonForm
from geotrek.core.fields import PointTopoGeomField, LineTopologyField, PointLineTopoGeomField
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
                }
            }
        )
    )
    topology_changed = BooleanField(required=False, widget=HiddenInput())
    geom_changed = BooleanField(required=False, widget=HiddenInput())

    class Meta(CommonForm.Meta):
        fields = [*CommonForm.Meta.fields, "topology", "geom", "topology_changed", "geom_changed"]

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

    def clean(self, *args, **kwargs):
        data = super().clean()
        geom = data.get("geom")
        geom_changed = data.get("geom_changed")
        topology_changed = data.get("topology_changed")

        if geom_changed and topology_changed:
            raise ValidationError(
                _(
                    "The geometry can only be drawn on or off the path network, not both."
                )
            )
        if geom_changed and isinstance(geom, LineString) and not self.is_drawing_off_path_network_allowed():
            raise ValidationError(_("You are not allowed to draw off the path network."))
        if self.instance.pk is None and not geom_changed and not topology_changed:
            # At creation, geometry and topology cannot both be None
            raise ValidationError(_("A geometry must be provided."))

        if topology_changed and "geom" in self.errors:
            del self.errors["geom"]
            # This geom will be overwritten be triggers
            data["geom"] = fromstr("POINT (0 0)")
        if geom_changed and "topology" in self.errors:
            del self.errors["topology"]
        if not geom_changed and geom is not None:
            data.pop("geom")

        return data

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
    geom = PointLineTopoGeomField(label="", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['geom'].widget.attrs["target_map"] = "topology"

    def disable_drawing_off_network_at_init(self):
        self.fields['geom'].widget.attrs["allowed_types"] = ["POINT"]

    def clean(self, *args, **kwargs):
        # If geom is a point topology, assign it to the topology field instead of the geom field
        data = super().clean()
        geom = data.get("geom")
        geom_changed = data.get("geom_changed")
        if geom_changed and isinstance(geom, Topology):
            data["topology"] = geom
            data["topology_changed"] = True
            data.pop("geom")
            data["geom_changed"] = False
        return data

    def save(self, *args, **kwargs):
        # Don't handle point geometries in parents' save methods -> save them as topologies is possible
        geom = None
        if self.cleaned_data.get("geom_changed"):
            geom = self.cleaned_data.get("geom")
            if isinstance(geom, Point):
                self.cleaned_data.pop("geom")

        instance = super().save(*args, **kwargs)

        if geom is not None and isinstance(geom, Topology):
            instance.mutate(geom)

        return instance
