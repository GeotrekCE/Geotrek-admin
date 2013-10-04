# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django_filters import CharFilter

from .models import Path

from geotrek.common.filters import OptionalRangeFilter
from geotrek.land.filters import EdgeStructureRelatedFilterSet


class PathFilter(EdgeStructureRelatedFilterSet):
    length = OptionalRangeFilter(label=_('length'))
    name = CharFilter(label=_('Name'), lookup_type='icontains')
    comments = CharFilter(label=_('Comments'), lookup_type='icontains')

    class Meta(EdgeStructureRelatedFilterSet.Meta):
        model = Path
        fields = EdgeStructureRelatedFilterSet.Meta.fields + [
                    'valid', 'length', 'networks', 'trail',
                ]
