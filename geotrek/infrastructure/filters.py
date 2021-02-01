from django.utils.translation import gettext_lazy as _
from django_filters import CharFilter

from geotrek.common.filters import StructureRelatedFilterSet, ValueFilter
from geotrek.infrastructure.widgets import InfrastructureYearSelect, InfrastructureImplantationYearSelect
from geotrek.maintenance.filters import InterventionYearTargetFilter
from .models import Infrastructure
from geotrek.zoning.filters import ZoningFilterSet


class InfrastructureFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    name = CharFilter(label=_('Name'), lookup_expr='icontains')
    description = CharFilter(label=_('Description'), lookup_expr='icontains')
    implantation_year = ValueFilter(field_name='implantation_year',
                                    widget=InfrastructureImplantationYearSelect)
    intervention_year = InterventionYearTargetFilter(widget=InfrastructureYearSelect)

    def __init__(self, *args, **kwargs):
        super(InfrastructureFilterSet, self).__init__(*args, **kwargs)

        field = self.form.fields['type__type']
        all_choices = list(field.widget.choices)
        field.widget.choices = [('', _("Category"))] + all_choices[1:]

    class Meta(StructureRelatedFilterSet.Meta):
        model = Infrastructure
        fields = StructureRelatedFilterSet.Meta.fields + ['type__type', 'type', 'condition', 'implantation_year',
                                                          'intervention_year', 'published']
