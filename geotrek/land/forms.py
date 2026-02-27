from django.conf import settings
from django.contrib.gis.forms import LineStringField

from geotrek.core.widgets import LineTopologyWidget

from .models import (
    CirculationEdge,
    CompetenceEdge,
    LandEdge,
    PhysicalEdge,
    SignageManagementEdge,
    WorkManagementEdge,
)

if settings.TREKKING_TOPOLOGY_ENABLED:
    from ..core.mixins.forms import TopologyForm as BaseForm
else:
    from geotrek.common.forms import CommonForm as BaseForm


class EdgeForm(BaseForm):
    if settings.TREKKING_TOPOLOGY_ENABLED:

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            modifiable = self.fields["topology"].widget.modifiable
            self.fields["topology"].widget = LineTopologyWidget()
            self.fields["topology"].widget.modifiable = modifiable
    else:
        geom = LineStringField()

        geom_fields = [
            "geom",
        ]

        class Meta(BaseForm.Meta):
            fields = [*BaseForm.Meta.fields, "geom"]


class PhysicalEdgeForm(EdgeForm):
    class Meta(EdgeForm.Meta):
        model = PhysicalEdge
        fields = [*EdgeForm.Meta.fields, "physical_type"]


class LandEdgeForm(EdgeForm):
    class Meta(EdgeForm.Meta):
        model = LandEdge
        fields = [*EdgeForm.Meta.fields, "land_type", "owner", "agreement"]


class CirculationEdgeForm(EdgeForm):
    class Meta(EdgeForm.Meta):
        model = CirculationEdge
        fields = [*EdgeForm.Meta.fields, "circulation_type", "authorization_type"]


class OrganismForm(EdgeForm):
    class Meta(EdgeForm.Meta):
        fields = [*EdgeForm.Meta.fields, "organization"]


class CompetenceEdgeForm(OrganismForm):
    class Meta(OrganismForm.Meta):
        model = CompetenceEdge


class WorkManagementEdgeForm(OrganismForm):
    class Meta(OrganismForm.Meta):
        model = WorkManagementEdge


class SignageManagementEdgeForm(OrganismForm):
    class Meta(OrganismForm.Meta):
        model = SignageManagementEdge
