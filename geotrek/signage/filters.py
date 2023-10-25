from django_filters import CharFilter, MultipleChoiceFilter, ModelMultipleChoiceFilter, ChoiceFilter
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from geotrek.altimetry.filters import AltimetryPointFilterSet
from geotrek.authent.models import Structure
from geotrek.common.models import Organism
from geotrek.core.models import Topology
from geotrek.core.filters import TopologyFilterTrail, ValidTopologyFilterSet
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.maintenance.models import Intervention
from geotrek.signage.models import Signage, Blade
from geotrek.zoning.filters import ZoningFilterSet

from mapentity.filters import MapEntityFilterSet, PolygonFilter


class PolygonTopologyFilter(PolygonFilter):
    def filter(self, qs, value):
        if not value:
            return qs
        lookup = self.lookup_expr
        inner_qs = Topology.objects.filter(**{'geom__%s' % lookup: value})
        return qs.filter(**{'%s__in' % self.field_name: inner_qs})


class SignageFilterSet(AltimetryPointFilterSet, ValidTopologyFilterSet, ZoningFilterSet, StructureRelatedFilterSet):
    name = CharFilter(label=_('Name'), lookup_expr='icontains')
    description = CharFilter(label=_('Description'), lookup_expr='icontains')
    implantation_year = MultipleChoiceFilter(choices=(('', '---------'),))
    intervention_year = MultipleChoiceFilter(label=_("Intervention year"), method='filter_intervention_year',
                                             choices=Intervention.objects.year_choices())
    trail = TopologyFilterTrail(label=_('Trail'), required=False)
    provider = ChoiceFilter(
        field_name='provider',
        empty_label=_("Provider"),
        label=_("Provider"),
        choices=(('', '---------'),)
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = Signage
        fields = StructureRelatedFilterSet.Meta.fields + ['type', 'condition', 'implantation_year', 'intervention_year',
                                                          'published', 'code', 'printed_elevation', 'manager',
                                                          'sealing', 'access', 'provider']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields['implantation_year'].choices = Signage.objects.implantation_year_choices()
        self.form.fields['provider'].choices = Signage.objects.provider_choices()

    def filter_intervention_year(self, qs, name, value):
        signage_ct = ContentType.objects.get_for_model(Signage)
        interventions = Intervention.objects.filter(target_type=signage_ct, date__year__in=value) \
            .values_list('target_id', flat=True)
        return qs.filter(id__in=interventions).distinct()


class BladeFilterSet(MapEntityFilterSet):
    bbox = PolygonTopologyFilter(field_name='topology', lookup_expr='intersects')
    structure = ModelMultipleChoiceFilter(field_name='signage__structure', queryset=Structure.objects.all(),
                                          help_text=_("Filter by one or more structure."))
    manager = ModelMultipleChoiceFilter(field_name='signage__manager', queryset=Organism.objects.all(),
                                        help_text=_("Filter by one or more manager."))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta(MapEntityFilterSet.Meta):
        model = Blade
        fields = MapEntityFilterSet.Meta.fields + ['structure', 'number', 'direction', 'type', 'color', 'condition']
