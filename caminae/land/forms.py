from caminae.core.forms import TopologyMixinForm

from .models import (PhysicalEdge, LandEdge, CompetenceEdge, WorkManagementEdge,
                    SignageManagementEdge)


class PhysicalEdgeForm(TopologyMixinForm):
    modelfields = ('physical_type',)

    class Meta(TopologyMixinForm.Meta):
        model = PhysicalEdge


class LandEdgeForm(TopologyMixinForm):
    modelfields = ('land_type',)

    class Meta(TopologyMixinForm.Meta):
        model = LandEdge


class OrganismForm(TopologyMixinForm):
    modelfields = ('organization',)
    class Meta(TopologyMixinForm.Meta):
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
