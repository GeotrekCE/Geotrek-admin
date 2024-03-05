from django.db.models.query_utils import Q
from django_filters import FilterSet
from django_filters.filters import BooleanFilter

from geotrek.authent.models import Structure
from geotrek.common.filters import ComaSeparatedMultipleModelChoiceFilter
from geotrek.common.models import TargetPortal
from geotrek.trekking.models import POI, Trek


class CirkwiPOIFilterSet(FilterSet):
    structures = ComaSeparatedMultipleModelChoiceFilter(field_name='structure', required=False,
                                                        queryset=Structure.objects.all())

    class Meta:
        model = POI
        fields = ('structures', )


class CirkwiTrekFilterSet(FilterSet):
    structures = ComaSeparatedMultipleModelChoiceFilter(field_name='structure', required=False,
                                                        queryset=Structure.objects.all())
    portals = ComaSeparatedMultipleModelChoiceFilter(field_name='portal', required=False,
                                                     queryset=TargetPortal.objects.all())
    include_externals = BooleanFilter(field_name='eid', method='filter_include_externals', required=False)

    def filter_include_externals(self, queryset, name, value):
        if not value:
            return queryset.filter(Q(eid__isnull=True) | Q(eid__exact=''))
        return queryset

    class Meta:
        model = Trek
        fields = ('structures', 'portals', )
