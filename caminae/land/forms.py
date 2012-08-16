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

    
class CompetenceEdgeForm(TopologyMixinForm):
    modelfields = ('organization',)

    class Meta(TopologyMixinForm.Meta):
        model = CompetenceEdge


class WorkManagementEdgeForm(TopologyMixinForm):
    modelfields = ('organization',)

    class Meta(TopologyMixinForm.Meta):
        model = WorkManagementEdge


class SignageManagementEdgeForm(TopologyMixinForm):
    modelfields = ('organization',)

    class Meta(TopologyMixinForm.Meta):
        model = SignageManagementEdge
