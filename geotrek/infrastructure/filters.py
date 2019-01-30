from django.utils.translation import ugettext_lazy as _
from django_filters import CharFilter

from geotrek.common.filters import StructureRelatedFilterSet, YearFilter, ValueFilter
from geotrek.infrastructure.widgets import InfrastructureYearSelect, InfrastructureImplantationYearSelect
from .models import Infrastructure


class InfrastructureFilterSet(StructureRelatedFilterSet):
    name = CharFilter(label=_('Name'), lookup_expr='icontains')
    description = CharFilter(label=_('Description'), lookup_expr='icontains')
    implantation_year = ValueFilter(name='implantation_year',
                                    widget=InfrastructureImplantationYearSelect)
    intervention_year = YearFilter(name='interventions_set__date',
                                   widget=InfrastructureYearSelect)

    def __init__(self, *args, **kwargs):
        super(InfrastructureFilterSet, self).__init__(*args, **kwargs)

        field = self.form.fields['type__type']
        all_choices = [field.widget.choices]
        all_choices = field.widget.choices
        all_choices = [c for c in all_choices]

    class Meta(StructureRelatedFilterSet.Meta):
        model = Infrastructure
        fields = StructureRelatedFilterSet.Meta.fields + ['type__type', 'type', 'condition', 'implantation_year',
                                                          'intervention_year', 'published']
