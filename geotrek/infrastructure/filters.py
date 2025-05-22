from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_filters import (
    CharFilter,
    ChoiceFilter,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
)

from geotrek.altimetry.filters import AltimetryAllGeometriesFilterSet
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.core.filters import TopologyFilterTrail, ValidTopologyFilterSet
from geotrek.maintenance.models import Intervention
from geotrek.zoning.filters import ZoningFilterSet

from .models import (
    Infrastructure,
    InfrastructureMaintenanceDifficultyLevel,
    InfrastructureTypeChoices,
    InfrastructureUsageDifficultyLevel,
)


class InfrastructureFilterSet(
    AltimetryAllGeometriesFilterSet,
    ValidTopologyFilterSet,
    ZoningFilterSet,
    StructureRelatedFilterSet,
):
    name = CharFilter(label=_("Name"), lookup_expr="icontains")
    description = CharFilter(label=_("Description"), lookup_expr="icontains")
    implantation_year = MultipleChoiceFilter(
        choices=lambda: Infrastructure.objects.implantation_year_choices()
    )
    intervention_year = MultipleChoiceFilter(
        label=_("Intervention year"),
        method="filter_intervention_year",
        choices=lambda: Intervention.objects.year_choices(),
    )
    category = MultipleChoiceFilter(
        label=_("Category"),
        field_name="type__type",
        choices=InfrastructureTypeChoices.choices,
    )
    trail = TopologyFilterTrail(label=_("Trail"), required=False)
    maintenance_difficulty = ModelMultipleChoiceFilter(
        queryset=InfrastructureMaintenanceDifficultyLevel.objects.all(),
        label=_("Maintenance difficulty"),
    )
    usage_difficulty = ModelMultipleChoiceFilter(
        queryset=InfrastructureUsageDifficultyLevel.objects.all(),
        label=_("Usage difficulty"),
    )
    provider = ChoiceFilter(
        field_name="provider",
        empty_label=_("Provider"),
        label=_("Provider"),
        choices=lambda: Infrastructure.objects.provider_choices(),
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = Infrastructure
        fields = [
            *StructureRelatedFilterSet.Meta.fields,
            "category",
            "type",
            "conditions",
            "implantation_year",
            "intervention_year",
            "published",
            "provider",
            "access",
        ]

    def filter_intervention_year(self, qs, name, value):
        infrastructure_ct = ContentType.objects.get_for_model(Infrastructure)
        q_1 = Q()
        for subvalue in value:
            # Intervention started in year 'subvalue', ended in year 'subvalue',
            # or was ongoing in year 'subvalue'
            q_1 = q_1 | Q(begin_date__year__lt=subvalue, end_date__year__gt=subvalue)
        q = Q(begin_date__year__in=value) | Q(end_date__year__in=value) | q_1
        q = Q(q, target_type=infrastructure_ct)
        interventions = Intervention.objects.filter(q).values_list(
            "target_id", flat=True
        )
        return qs.filter(id__in=interventions).distinct()
