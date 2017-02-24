from django.utils.translation import ugettext_lazy as _
from django_filters import CharFilter, NumberFilter

from geotrek.common.filters import StructureRelatedFilterSet, YearFilter
from geotrek.maintenance.filters import InterventionYearSelect
from .models import INFRASTRUCTURE_TYPES, Infrastructure, Signage


class InfrastructureYearSelect(InterventionYearSelect):
    label = _(u"Intervention year")


class InfrastructureFilterSet(StructureRelatedFilterSet):
    name = CharFilter(label=_('Name'), lookup_expr='icontains')
    description = CharFilter(label=_('Description'), lookup_expr='icontains')
    implantation_year = NumberFilter(label=_('Implantation year'))
    intervention_year = YearFilter(name='interventions_set__date',
                                   widget=InfrastructureYearSelect)

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
        fields = StructureRelatedFilterSet.Meta.fields + ['type__type', 'type', 'condition', 'implantation_year']


class SignageFilterSet(StructureRelatedFilterSet):
    name = CharFilter(label=_('Name'), lookup_expr='icontains')
    description = CharFilter(label=_('Description'), lookup_expr='icontains')
    implantation_year = NumberFilter(label=_('Implantation year'))
    intervention_year = YearFilter(name='interventions_set__date',
                                   widget=InfrastructureYearSelect)

    def __init__(self, *args, **kwargs):
        super(SignageFilterSet, self).__init__(*args, **kwargs)
        field = self.form.fields['type']
        field.queryset = field.queryset.filter(type=INFRASTRUCTURE_TYPES.SIGNAGE)

    class Meta(StructureRelatedFilterSet.Meta):
        model = Signage
        fields = StructureRelatedFilterSet.Meta.fields + ['type', 'condition', 'implantation_year']
