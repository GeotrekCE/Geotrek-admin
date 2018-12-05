from geotrek.core.widgets import LineTopologyWidget
from geotrek.core.forms import TopologyForm
from .models import (PhysicalEdge, LandEdge, CompetenceEdge, WorkManagementEdge,
                     SignageManagementEdge)


class EdgeForm(TopologyForm):
    def __init__(self, *args, **kwargs):
        super(EdgeForm, self).__init__(*args, **kwargs)
        self.fields['topology'].widget = LineTopologyWidget()


class PhysicalEdgeForm(EdgeForm):
    class Meta(EdgeForm.Meta):
        model = PhysicalEdge
        fields = EdgeForm.Meta.fields + ['physical_type']


class LandEdgeForm(EdgeForm):
    class Meta(EdgeForm.Meta):
        model = LandEdge
        fields = EdgeForm.Meta.fields + ['land_type', 'owner', 'agreement']


class OrganismForm(EdgeForm):
    class Meta(EdgeForm.Meta):
        fields = EdgeForm.Meta.fields + ['organization']


class CompetenceEdgeForm(OrganismForm):
    class Meta(OrganismForm.Meta):
        model = CompetenceEdge


class WorkManagementEdgeForm(OrganismForm):
    class Meta(OrganismForm.Meta):
        model = WorkManagementEdge


class SignageManagementEdgeForm(OrganismForm):
    class Meta(OrganismForm.Meta):
        model = SignageManagementEdge
