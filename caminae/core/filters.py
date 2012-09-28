# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django_filters import CharFilter

from .models import Path

from caminae.common.filters import OptionalRangeFilter, StructureRelatedFilterSet
from caminae.land.filters import (
        TopoFilterPhysicalType, TopoFilterLandType,
        TopoFilterCompetenceEdge, TopoFilterSignageManagementEdge, TopoFilterWorkManagementEdge
)

class PathFilter(StructureRelatedFilterSet):
    length = OptionalRangeFilter(label=_('length'))   # TODO: why force ?
    name = CharFilter(label=_('Name'), lookup_type='icontains')
    comments = CharFilter(label=_('Comments'), lookup_type='icontains')

    physical_type = TopoFilterPhysicalType(label=_('Physical type'), required=False)
    land_type = TopoFilterLandType(label=_('Land type'), required=False)

    competence = TopoFilterCompetenceEdge(label=_('Competence'), required=False)
    signage = TopoFilterSignageManagementEdge(label=_('Signage management'), required=False)
    work = TopoFilterWorkManagementEdge(label=_('Work management'), required=False)

    class Meta(StructureRelatedFilterSet.Meta):
        model = Path
        fields = StructureRelatedFilterSet.Meta.fields + [
                    'length', 'networks', 'trail',
                ]


