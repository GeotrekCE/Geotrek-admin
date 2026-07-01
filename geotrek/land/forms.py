from ..common.forms import CommonForm
from ..core.mixins.forms import LineTopologyFormMixin
from .models import (
    CirculationEdge,
    CompetenceEdge,
    LandEdge,
    PhysicalEdge,
    SignageManagementEdge,
    WorkManagementEdge,
)


class PhysicalEdgeForm(LineTopologyFormMixin):
    class Meta(LineTopologyFormMixin.Meta):
        model = PhysicalEdge
        fields = [*LineTopologyFormMixin.Meta.fields, "physical_type"]


class LandEdgeForm(LineTopologyFormMixin):
    class Meta(LineTopologyFormMixin.Meta):
        model = LandEdge
        fields = [
            *LineTopologyFormMixin.Meta.fields,
            "land_type",
            "owner",
            "agreement",
        ]


class CirculationEdgeForm(LineTopologyFormMixin):
    class Meta(LineTopologyFormMixin.Meta):
        model = CirculationEdge
        fields = [
            *LineTopologyFormMixin.Meta.fields,
            "circulation_type",
            "authorization_type",
        ]


class CompetenceEdgeForm(LineTopologyFormMixin):
    class Meta(LineTopologyFormMixin.Meta):
        model = CompetenceEdge
        fields = [*LineTopologyFormMixin.Meta.fields, "organization"]


class WorkManagementEdgeForm(LineTopologyFormMixin):
    class Meta(LineTopologyFormMixin.Meta):
        model = WorkManagementEdge
        fields = [*LineTopologyFormMixin.Meta.fields, "organization"]


class SignageManagementEdgeForm(LineTopologyFormMixin):
    class Meta(LineTopologyFormMixin.Meta):
        model = SignageManagementEdge
        fields = [*LineTopologyFormMixin.Meta.fields, "organization"]
