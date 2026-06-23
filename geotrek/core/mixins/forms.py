from copy import deepcopy

from django.conf import settings
from django.contrib.gis.forms import LineStringField
from django.contrib.gis.geos import fromstr
from django.forms import BooleanField, HiddenInput, ModelForm, ValidationError
from django.utils.translation import gettext_lazy as _

from geotrek.common.forms import CommonForm
from geotrek.core.fields import PointTopologyField, TopologyField
from geotrek.core.widgets import LinearTopologyMapWidget, LineTopologyWidget


# TODO: delete
class TopologyForm(CommonForm):
    """
    This form is a bit specific :

        We use an extra field (topology) in order to edit the whole model instance.
        The whole instance, because we use concrete inheritance for topology models.
        Thus, at init, we load the instance into field, and at save, we
        save the field into the instance.

    The geom field is fully ignored, since we edit a topology.
    """

    topology = TopologyField(label="")
    geomfields = ["topology"]

    class Meta(CommonForm.Meta):
        fields = [*CommonForm.Meta.fields, "topology"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["topology"].initial = self.instance

    def clean(self, *args, **kwargs):
        data = super().clean()
        # geom is computed at db-level and never edited
        if "geom" in self.errors:
            del self.errors["geom"]
        return data

    def save(self, *args, **kwargs):
        topology = self.cleaned_data.pop("topology")
        instance = super().save(*args, **kwargs)
        was_edited = instance.pk != topology.pk
        if was_edited:
            instance.mutate(topology)
        return instance


class PointTopologyFormMixin(CommonForm):
    """
    Form mixin for drawing points, on or off the path network depending on whether paths exist.
    """

    geomfields = ["topology"]
    topology = PointTopologyField(label="")

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


class LinearTopologyFormMixin(ModelForm):
    """
    Form mixin for drawing linear topologies on or off the path network, depending on:
      - whether paths exist
      - the user's permissions
    """

    topology = TopologyField(required=False, label="", widget=LineTopologyWidget())
    topology_changed = BooleanField(required=False, widget=HiddenInput())
    geom = LineStringField(
        required=False, widget=LinearTopologyMapWidget(attrs={"target_map": "topology"})
    )
    geom_changed = BooleanField(required=False, widget=HiddenInput())
    geomfields = ["topology", "geom"]

    class Meta:
        fields = ["topology", "geom", "topology_changed", "geom_changed"]

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
            self.fields["geom"].disabled = True
            self.fields["geom"].widget = LinearTopologyMapWidget(
                attrs={"target_map": "topology", "modifiable": False}
            )
            self.fields.pop("geom_changed")

    def is_drawing_off_path_network_allowed(self):
        if not settings.PATH_MODEL_ENABLED:
            return True
        return self.user.has_perm("core.can_draw_off_path_network")

    def clean(self, *args, **kwargs):
        data = super().clean()
        geom_changed = data.get("geom_changed")
        topology_changed = data.get("topology_changed")

        if geom_changed and topology_changed:
            raise ValidationError(
                _(
                    "The geometry can only be drawn on or off the path network, not both."
                )
            )
        # At creation, geometry and topology cannot both be None:
        if self.instance.pk is None and not geom_changed and not topology_changed:
            raise ValidationError(_("A geometry must be provided."))

        if topology_changed and "geom" in self.errors:
            del self.errors["geom"]
            data["geom"] = fromstr("POINT (0 0)")
        if geom_changed and "topology" in self.errors:
            del self.errors["topology"]
        if not geom_changed:
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
