from django.utils.translation import ugettext_lazy as _

from mapentity.filters import YearFilter
from geotrek.land.filters import EdgeStructureRelatedFilterSet
from geotrek.maintenance.filters import InterventionYearSelect

from .models import INFRASTRUCTURE_TYPES, Infrastructure, Signage


class InfrastructureFilter(EdgeStructureRelatedFilterSet):
    intervention_year = YearFilter(name='interventions_set__date',
                                   widget=InterventionYearSelect,
                                   label=_(u"Intervention year"))

    def __init__(self, *args, **kwargs):
        super(InfrastructureFilter, self).__init__(*args, **kwargs)
        field = self.form.fields['type']
        field.queryset = field.queryset.exclude(type=INFRASTRUCTURE_TYPES.SIGNAGE)

    class Meta(EdgeStructureRelatedFilterSet.Meta):
        model = Infrastructure
        fields = EdgeStructureRelatedFilterSet.Meta.fields + ['type__type', 'type']


class SignageFilter(EdgeStructureRelatedFilterSet):
    intervention_year = YearFilter(name='interventions_set__date',
                                   widget=InterventionYearSelect,
                                   label=_(u"Intervention year"))

    def __init__(self, *args, **kwargs):
        super(SignageFilter, self).__init__(*args, **kwargs)
        field = self.form.fields['type']
        field.queryset = field.queryset.filter(type=INFRASTRUCTURE_TYPES.SIGNAGE)

    class Meta(EdgeStructureRelatedFilterSet.Meta):
        model = Signage
        fields = EdgeStructureRelatedFilterSet.Meta.fields + ['type']
