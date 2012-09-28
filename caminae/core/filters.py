# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django_filters import CharFilter

from .models import Path

from caminae.common.filters import OptionalRangeFilter
from caminae.land.filters import EdgeFilter


class PathFilter(EdgeFilter):
    length = OptionalRangeFilter(label=_('length'))   # TODO: why force ?
    name = CharFilter(label=_('Name'), lookup_type='icontains')
    comments = CharFilter(label=_('Comments'), lookup_type='icontains')

    class Meta(EdgeFilter.Meta):
        model = Path
        fields = EdgeFilter.Meta.fields + [
                    'length', 'networks', 'trail',
                ]


