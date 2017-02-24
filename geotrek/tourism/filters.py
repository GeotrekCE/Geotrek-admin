from django.utils.translation import ugettext_lazy as _

import django_filters
import django_filters.rest_framework
from django.db.models import Q
from geotrek.common.filters import StructureRelatedFilterSet
from django.utils.datetime_safe import datetime

from .models import TouristicContent, TouristicEvent


class TouristicContentFilterSet(StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = TouristicContent
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'category', 'themes', 'type1',
            'type2', 'approved', 'source', 'portal'
        ]


class AfterFilter(django_filters.DateFilter):
    def filter(self, qs, value):
        return qs.filter(end_date__gte=value)


class BeforeFilter(django_filters.DateFilter):
    def filter(self, qs, value):
        return qs.filter(begin_date__lte=value)


class CompletedFilter(django_filters.BooleanFilter):
    """
    Filter events with end_date in past (event completed)
    """
    @property
    def field(self):
        field = super(CompletedFilter, self).field
        field.initial = False
        return field

    def filter(self, qs, value):
        queryset = qs

        if value is True:
            queryset = queryset.filter(end_date__lt=datetime.today)

        elif value is False:
            queryset = queryset.exclude(end_date__lt=datetime.today)

        return queryset


class TouristicEventFilterSet(StructureRelatedFilterSet):
    after = AfterFilter(label=_(u"After"))
    before = BeforeFilter(label=_(u"Before"))
    completed = CompletedFilter(label=_(u"Completed"))

    class Meta(StructureRelatedFilterSet.Meta):
        model = TouristicEvent
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'type', 'themes', 'after',
            'before', 'approved', 'source', 'portal'
        ]


class TouristicEventApiFilterSet(django_filters.rest_framework.FilterSet):
    ends_after = django_filters.DateFilter(method='events_end_after')

    class Meta:
        model = TouristicEvent
        fields = ('ends_after', )

    def events_end_after(self, queryset, name, value):
        return queryset.filter(
            Q(end_date__isnull=True) |
            Q(end_date__gte=value)
        )
