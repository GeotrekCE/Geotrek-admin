from django.utils.translation import ugettext_lazy as _

from mapentity.filters import YearFilter
from geotrek.land.filters import EdgeStructureRelatedFilterSet
from geotrek.maintenance.filters import InterventionYearSelect

from .models import INFRASTRUCTURE_TYPES, Infrastructure, Signage


class InfrastructureFilterSet(EdgeStructureRelatedFilterSet):
    intervention_year = YearFilter(name='interventions_set__date',
                                   widget=InterventionYearSelect,
                                   label=_(u"Intervention year"))

    def __init__(self, *args, **kwargs):
        super(InfrastructureFilterSet, self).__init__(*args, **kwargs)
        field = self.form.fields['type']
        field.queryset = field.queryset.exclude(type=INFRASTRUCTURE_TYPES.SIGNAGE)

    class Meta(EdgeStructureRelatedFilterSet.Meta):
        model = Infrastructure
        fields = EdgeStructureRelatedFilterSet.Meta.fields + ['type__type', 'type']


class SignageFilterSet(EdgeStructureRelatedFilterSet):
    intervention_year = YearFilter(name='interventions_set__date',
                                   widget=InterventionYearSelect,
                                   label=_(u"Intervention year"))

    def __init__(self, *args, **kwargs):
        super(SignageFilterSet, self).__init__(*args, **kwargs)
        field = self.form.fields['type']
        field.queryset = field.queryset.filter(type=INFRASTRUCTURE_TYPES.SIGNAGE)

    class Meta(EdgeStructureRelatedFilterSet.Meta):
        model = Signage
        fields = EdgeStructureRelatedFilterSet.Meta.fields + ['type']
