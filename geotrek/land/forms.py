from ..common.forms import CommonForm
from ..core.mixins.forms import LinearTopologyFormMixin
from .models import (
    CirculationEdge,
    CompetenceEdge,
    LandEdge,
    PhysicalEdge,
    SignageManagementEdge,
    WorkManagementEdge,
)


class PhysicalEdgeForm(LinearTopologyFormMixin, CommonForm):
    class Meta(LinearTopologyFormMixin.Meta):
        model = PhysicalEdge
        fields = [*LinearTopologyFormMixin.Meta.fields, "physical_type"]


class LandEdgeForm(LinearTopologyFormMixin, CommonForm):
    class Meta(LinearTopologyFormMixin.Meta):
        model = LandEdge
        fields = [
            *LinearTopologyFormMixin.Meta.fields,
            "land_type",
            "owner",
            "agreement",
        ]


class CirculationEdgeForm(LinearTopologyFormMixin, CommonForm):
    class Meta(LinearTopologyFormMixin.Meta):
        model = CirculationEdge
        fields = [
            *LinearTopologyFormMixin.Meta.fields,
            "circulation_type",
            "authorization_type",
        ]


class CompetenceEdgeForm(LinearTopologyFormMixin, CommonForm):
    class Meta(LinearTopologyFormMixin.Meta):
        model = CompetenceEdge
        fields = [*LinearTopologyFormMixin.Meta.fields, "organization"]


class WorkManagementEdgeForm(LinearTopologyFormMixin, CommonForm):
    class Meta(LinearTopologyFormMixin.Meta):
        model = WorkManagementEdge
        fields = [*LinearTopologyFormMixin.Meta.fields, "organization"]


class SignageManagementEdgeForm(LinearTopologyFormMixin, CommonForm):
    class Meta(LinearTopologyFormMixin.Meta):
        model = SignageManagementEdge
        fields = [*LinearTopologyFormMixin.Meta.fields, "organization"]
