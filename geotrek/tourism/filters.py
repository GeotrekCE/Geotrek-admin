from django.utils.translation import ugettext_lazy as _

import django_filters

from geotrek.common.filters import StructureRelatedFilterSet

from .models import TouristicContent, TouristicEvent


class TouristicContentFilterSet(StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = TouristicContent
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'category', 'themes', 'type1', 'type2', 'approved']


class AfterFilter(django_filters.DateFilter):
    def filter(self, qs, value):
        return qs.filter(end_date__gte=value)


class BeforeFilter(django_filters.DateFilter):
    def filter(self, qs, value):
        return qs.filter(begin_date__lte=value)


class TouristicEventFilterSet(StructureRelatedFilterSet):
    after = AfterFilter(label=_(u"After"))
    before = BeforeFilter(label=_(u"Before"))

    class Meta(StructureRelatedFilterSet.Meta):
        model = TouristicEvent
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'type', 'themes', 'after', 'before', 'approved']


class TouristicEventApiFilterSet(django_filters.FilterSet):
    ends_after = django_filters.DateFilter('end_date', lookup_type='gte')

    class Meta:
        model = TouristicEvent
        fields = ['end_date', ]
