from .models import (
    CirculationEdge,
    CompetenceEdge,
    LandEdge,
    PhysicalEdge,
    SignageManagementEdge,
    WorkManagementEdge,
)
from ..common.forms import CommonForm

from ..core.mixins.forms import OnNetworkLinearTopologyFormMixin, OffNetworkLinearTopologyFormMixin


class OnNetworkPhysicalEdgeForm(OnNetworkLinearTopologyFormMixin, CommonForm):
    class Meta(OnNetworkLinearTopologyFormMixin.Meta):
        model = PhysicalEdge
        fields = [*OnNetworkLinearTopologyFormMixin.Meta.fields, "physical_type"]


class OffNetworkPhysicalEdgeForm(OffNetworkLinearTopologyFormMixin, CommonForm):
    class Meta(OffNetworkLinearTopologyFormMixin.Meta):
        model = PhysicalEdge
        fields = [*OffNetworkLinearTopologyFormMixin.Meta.fields, "physical_type"]


class OnNetworkLandEdgeForm(OnNetworkLinearTopologyFormMixin, CommonForm):
    class Meta(OnNetworkLinearTopologyFormMixin.Meta):
        model = LandEdge
        fields = [*OnNetworkLinearTopologyFormMixin.Meta.fields, "land_type", "owner", "agreement"]


class OffNetworkLandEdgeForm(OffNetworkLinearTopologyFormMixin, CommonForm):
    class Meta(OffNetworkLinearTopologyFormMixin.Meta):
        model = LandEdge
        fields = [*OffNetworkLinearTopologyFormMixin.Meta.fields, "land_type", "owner", "agreement"]


class OnNetworkCirculationEdgeForm(OnNetworkLinearTopologyFormMixin, CommonForm):
    class Meta(OnNetworkLinearTopologyFormMixin.Meta):
        model = CirculationEdge
        fields = [*OnNetworkLinearTopologyFormMixin.Meta.fields, "circulation_type", "authorization_type"]


class OffNetworkCirculationEdgeForm(OffNetworkLinearTopologyFormMixin, CommonForm):
    class Meta(OffNetworkLinearTopologyFormMixin.Meta):
        model = CirculationEdge
        fields = [*OffNetworkLinearTopologyFormMixin.Meta.fields, "circulation_type", "authorization_type"]


class OnNetworkCompetenceEdgeForm(OnNetworkLinearTopologyFormMixin, CommonForm):
    class Meta(OnNetworkLinearTopologyFormMixin.Meta):
        model = CompetenceEdge
        fields = [*OnNetworkLinearTopologyFormMixin.Meta.fields, "organization"]


class OffNetworkCompetenceEdgeForm(OffNetworkLinearTopologyFormMixin, CommonForm):
    class Meta(OffNetworkLinearTopologyFormMixin.Meta):
        model = CompetenceEdge
        fields = [*OffNetworkLinearTopologyFormMixin.Meta.fields, "organization"]


class OnNetworkWorkManagementEdgeForm(OnNetworkLinearTopologyFormMixin, CommonForm):
    class Meta(OnNetworkLinearTopologyFormMixin.Meta):
        model = WorkManagementEdge
        fields = [*OnNetworkLinearTopologyFormMixin.Meta.fields, "organization"]


class OffNetworkWorkManagementEdgeForm(OffNetworkLinearTopologyFormMixin, CommonForm):
    class Meta(OffNetworkLinearTopologyFormMixin.Meta):
        model = WorkManagementEdge
        fields = [*OffNetworkLinearTopologyFormMixin.Meta.fields, "organization"]


class OnNetworkSignageManagementEdgeForm(OnNetworkLinearTopologyFormMixin, CommonForm):
    class Meta(OnNetworkLinearTopologyFormMixin.Meta):
        model = SignageManagementEdge
        fields = [*OnNetworkLinearTopologyFormMixin.Meta.fields, "organization"]


class OffNetworkSignageManagementEdgeForm(OffNetworkLinearTopologyFormMixin, CommonForm):
    class Meta(OffNetworkLinearTopologyFormMixin.Meta):
        model = SignageManagementEdge
        fields = [*OffNetworkLinearTopologyFormMixin.Meta.fields, "organization"]
