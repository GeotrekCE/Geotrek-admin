from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_filters import (
    CharFilter,
    ChoiceFilter,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
)
from mapentity.filters import MapEntityFilterSet, PolygonFilter

from geotrek.altimetry.filters import AltimetryPointFilterSet
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.authent.models import Structure
from geotrek.common.models import Organism
from geotrek.core.filters import TopologyFilterTrail, ValidTopologyFilterSet
from geotrek.core.models import Topology
from geotrek.maintenance.models import Intervention
from geotrek.signage.models import Blade, Signage
from geotrek.zoning.filters import ZoningFilterSet


class PolygonTopologyFilter(PolygonFilter):
    def filter(self, qs, value):
        if not value:
            return qs
        lookup = self.lookup_expr
        inner_qs = Topology.objects.filter(**{f"geom__{lookup}": value})
        return qs.filter(**{f"{self.field_name}__in": inner_qs})


class SignageFilterSet(
    AltimetryPointFilterSet,
    ValidTopologyFilterSet,
    ZoningFilterSet,
    StructureRelatedFilterSet,
):
    name = CharFilter(label=_("Name"), lookup_expr="icontains")
    code = CharFilter(label=_("Code"), lookup_expr="icontains")
    description = CharFilter(label=_("Description"), lookup_expr="icontains")
    implantation_year = MultipleChoiceFilter(
        choices=lambda: Signage.objects.implantation_year_choices()
    )
    intervention_year = MultipleChoiceFilter(
        label=_("Intervention year"),
        method="filter_intervention_year",
        choices=lambda: Intervention.objects.year_choices(),
    )
    trail = TopologyFilterTrail(label=_("Trail"), required=False)
    provider = ChoiceFilter(
        field_name="provider",
        empty_label=_("Provider"),
        label=_("Provider"),
        choices=lambda: Signage.objects.provider_choices(),
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = Signage
        fields = [
            *StructureRelatedFilterSet.Meta.fields,
            "type",
            "conditions",
            "implantation_year",
            "intervention_year",
            "published",
            "code",
            "printed_elevation",
            "manager",
            "sealing",
            "access",
            "provider",
        ]

    def filter_intervention_year(self, qs, name, value):
        signage_ct = ContentType.objects.get_for_model(Signage)
        q_1 = Q()
        for subvalue in value:
            # Intervention started in year 'subvalue', ended in year 'subvalue',
            # or was ongoing in year 'subvalue'
            q_1 = q_1 | Q(begin_date__year__lt=subvalue, end_date__year__gt=subvalue)
        q = Q(begin_date__year__in=value) | Q(end_date__year__in=value) | q_1
        q = Q(q, target_type=signage_ct)
        interventions = Intervention.objects.filter(q).values_list(
            "target_id", flat=True
        )
        return qs.filter(id__in=interventions).distinct()


class BladeFilterSet(MapEntityFilterSet):
    bbox = PolygonTopologyFilter(field_name="topology", lookup_expr="intersects")
    structure = ModelMultipleChoiceFilter(
        field_name="signage__structure",
        queryset=Structure.objects.all(),
        help_text=_("Filter by one or more structure."),
    )
    manager = ModelMultipleChoiceFilter(
        field_name="signage__manager",
        queryset=Organism.objects.all(),
        help_text=_("Filter by one or more manager."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta(MapEntityFilterSet.Meta):
        model = Blade
        fields = [
            *MapEntityFilterSet.Meta.fields,
            "structure",
            "number",
            "direction",
            "type",
            "color",
            "conditions",
        ]
