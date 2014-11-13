from django.utils.translation import ugettext_lazy as _

from geotrek.common.filters import StructureRelatedFilterSet, YearFilter
from geotrek.maintenance.filters import InterventionYearSelect

from .models import INFRASTRUCTURE_TYPES, Infrastructure, Signage


class InfrastructureYearSelect(InterventionYearSelect):
    label = _(u"Intervention year")


class InfrastructureFilterSet(StructureRelatedFilterSet):
    intervention_year = YearFilter(name='interventions_set__date',
                                   widget=InfrastructureYearSelect,
                                   label=_(u"Intervention year"))

    def __init__(self, *args, **kwargs):
        super(InfrastructureFilterSet, self).__init__(*args, **kwargs)
        field = self.form.fields['type']
        field.queryset = field.queryset.exclude(type=INFRASTRUCTURE_TYPES.SIGNAGE)

        field = self.form.fields['type__type']
        all_choices = field.widget.choices
        all_choices = [c for c in all_choices if c[0] != INFRASTRUCTURE_TYPES.SIGNAGE]
        field.widget.choices = [('', _(u"Category"))] + all_choices

    class Meta(StructureRelatedFilterSet.Meta):
        model = Infrastructure
        fields = StructureRelatedFilterSet.Meta.fields + ['type__type', 'type']


class SignageFilterSet(StructureRelatedFilterSet):
    intervention_year = YearFilter(name='interventions_set__date',
                                   widget=InfrastructureYearSelect)

    class Meta(StructureRelatedFilterSet.Meta):
        model = Signage
        fields = StructureRelatedFilterSet.Meta.fields
