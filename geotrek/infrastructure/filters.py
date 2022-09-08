from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django_filters import CharFilter, MultipleChoiceFilter, ModelMultipleChoiceFilter, ChoiceFilter
from geotrek.altimetry.filters import AltimetryAllGeometriesFilterSet
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.core.filters import ValidTopologyFilterSet, TopologyFilterTrail
from .models import Infrastructure, INFRASTRUCTURE_TYPES, InfrastructureMaintenanceDifficultyLevel, InfrastructureUsageDifficultyLevel
from geotrek.maintenance.models import Intervention
from geotrek.zoning.filters import ZoningFilterSet


class InfrastructureFilterSet(AltimetryAllGeometriesFilterSet, ValidTopologyFilterSet, ZoningFilterSet, StructureRelatedFilterSet):
    name = CharFilter(label=_('Name'), lookup_expr='icontains')
    description = CharFilter(label=_('Description'), lookup_expr='icontains')
    implantation_year = MultipleChoiceFilter(choices=Infrastructure.objects.implantation_year_choices())
    intervention_year = MultipleChoiceFilter(label=_("Intervention year"), method='filter_intervention_year',
                                             choices=Intervention.objects.year_choices())
    category = MultipleChoiceFilter(label=_("Category"), field_name='type__type',
                                    choices=INFRASTRUCTURE_TYPES)
    trail = TopologyFilterTrail(label=_('Trail'), required=False)
    maintenance_difficulty = ModelMultipleChoiceFilter(queryset=InfrastructureMaintenanceDifficultyLevel.objects.all(), label=_("Maintenance difficulty"))
    usage_difficulty = ModelMultipleChoiceFilter(queryset=InfrastructureUsageDifficultyLevel.objects.all(), label=_("Usage difficulty"))
    provider = ChoiceFilter(
        field_name='provider',
        empty_label=_("Provider"),
        label=_("Provider"),
        choices=Infrastructure.objects.provider_choices()
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = Infrastructure
        fields = StructureRelatedFilterSet.Meta.fields + [
            'category', 'type', 'condition', 'implantation_year',
            'intervention_year', 'published', 'provider'
        ]

    def filter_intervention_year(self, qs, name, value):
        infrastructure_ct = ContentType.objects.get_for_model(Infrastructure)
        interventions = Intervention.objects.filter(target_type=infrastructure_ct, date__year__in=value) \
            .values_list('target_id', flat=True)
        return qs.filter(id__in=interventions).distinct()
