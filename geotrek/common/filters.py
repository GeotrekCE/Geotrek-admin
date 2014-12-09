import sys
from decimal import Decimal

from django.utils.translation import ugettext_lazy as _

from django_filters import RangeFilter, Filter
from mapentity.filters import MapEntityFilterSet


class OptionalRangeFilter(RangeFilter):
    def __init__(self, *args, **kwargs):
        super(OptionalRangeFilter, self).__init__(*args, **kwargs)
        self.field.fields[0].label = _('min %s') % self.field.label
        self.field.fields[1].label = _('max %s') % self.field.label

    def filter(self, qs, value):
        if value:
            if value.start and not value.stop:
                value = slice(value.start, Decimal(sys.maxint), value.step)
            if not value.start and value.stop:
                value = slice(Decimal(-(sys.maxint + 1)), value.stop, value.step)
        return super(OptionalRangeFilter, self).filter(qs, value)


class YearFilter(Filter):
    def do_filter(self, qs, year):
        return qs.filter(**{
            '%s__year' % self.name: year,
        }).distinct()

    def filter(self, qs, value):
        try:
            year = int(value)
        except (ValueError, TypeError):
            year = -1
        return qs if year < 0 else self.do_filter(qs, year)


class YearBetweenFilter(YearFilter):
    def __init__(self, *args, **kwargs):
        assert len(kwargs['name']) == 2
        super(YearBetweenFilter, self).__init__(*args, **kwargs)

    def do_filter(self, qs, year):
        begin, end = self.name
        qs = qs.filter(**{
            '%s__lte' % begin: year,
            '%s__gte' % end: year,
        })
        return qs


class StructureRelatedFilterSet(MapEntityFilterSet):
    class Meta(MapEntityFilterSet.Meta):
        fields = MapEntityFilterSet.Meta.fields + ['structure']
