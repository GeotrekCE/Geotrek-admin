from caminae.core.forms import TopologyMixinForm

from .models import (PhysicalEdge, LandEdge, CompetenceEdge, WorkManagementEdge,
                    SignageManagementEdge)


class PhysicalEdgeForm(TopologyMixinForm):
    modelfields = (
            'physical_type',
            )
    geomfields = ('geom', )
    
    class Meta:
        model = PhysicalEdge
        exclude = ('deleted', 'kind', 'troncons', 'offset')


class LandEdgeForm(TopologyMixinForm):
    modelfields = (
            'land_type',
            )
    geomfields = ('geom', )
    
    class Meta:
        model = LandEdge
        exclude = ('deleted', 'kind', 'troncons', 'offset')

    
class CompetenceEdgeForm(TopologyMixinForm):
    modelfields = (
            'organization',
            )
    geomfields = ('geom', )
    
    class Meta:
        model = CompetenceEdge
        exclude = ('deleted', 'kind', 'troncons', 'offset')


class WorkManagementEdgeForm(TopologyMixinForm):
    modelfields = (
            'organization',
            )
    geomfields = ('geom', )
    
    class Meta:
        model = WorkManagementEdge
        exclude = ('deleted', 'kind', 'troncons', 'offset')


class SignageManagementEdgeForm(TopologyMixinForm):
    modelfields = (
            'organization',
            )
    geomfields = ('geom', )
    
    class Meta:
        model = SignageManagementEdge
        exclude = ('deleted', 'kind', 'troncons', 'offset')
