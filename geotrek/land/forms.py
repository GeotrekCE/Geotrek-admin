from geotrek.core.widgets import LineTopologyWidget
from geotrek.core.forms import TopologyForm

from .models import (PhysicalEdge, LandEdge, CompetenceEdge, WorkManagementEdge,
                    SignageManagementEdge)


class EdgeForm(TopologyForm):
    def __init__(self, *args, **kwargs):
        super(EdgeForm, self).__init__(*args, **kwargs)
        self.fields['topology'].widget = LineTopologyWidget()


class PhysicalEdgeForm(EdgeForm):
    modelfields = ('physical_type',)

    class Meta(EdgeForm.Meta):
        model = PhysicalEdge


class LandEdgeForm(EdgeForm):
    modelfields = ('land_type',)

    class Meta(EdgeForm.Meta):
        model = LandEdge


class OrganismForm(EdgeForm):
    modelfields = ('organization',)
    class Meta(EdgeForm.Meta):
        pass


class CompetenceEdgeForm(OrganismForm):
    class Meta(OrganismForm.Meta):
        model = CompetenceEdge


class WorkManagementEdgeForm(OrganismForm):
    class Meta(OrganismForm.Meta):
        model = WorkManagementEdge


class SignageManagementEdgeForm(OrganismForm):
    class Meta(OrganismForm.Meta):
        model = SignageManagementEdge
