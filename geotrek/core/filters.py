from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django_filters import CharFilter, ModelChoiceFilter

from .models import Topology, Path, Trail

from geotrek.common.filters import OptionalRangeFilter, StructureRelatedFilterSet, RightFilter
from geotrek.infrastructure.filters import InfrastructureFilterSet
from geotrek.signage.filters import SignageFilterSet
from geotrek.maintenance.filters import InterventionFilterSet, ProjectFilterSet
from geotrek.maintenance import models as maintenance_models


class TopologyFilter(RightFilter):
    def filter(self, qs, value):
        """Overrides parent filter() method completely.
        """
        if not value:
            return qs
        if issubclass(value.__class__, Topology):
            edges = Topology.objects.filter(pk=value.pk)
        else:
            edges = self.value_to_edges(value)
        return self._topology_filter(qs, edges)

    def value_to_edges(self, value):
        """
        For an instance of this filter model, returns a Topology queryset.
        """
        raise NotImplementedError

    def _topology_filter(self, qs, edges):
        """
        This piece of code should be rewritten nicely with managers : TODO !
        """
        # In case, we filter on paths
        if qs.model == Path:
            paths = []
            for edge in edges:
                paths.extend(edge.paths.all())
            return qs.filter(pk__in=[path.pk for path in set(paths)])

        overlapping = Topology.overlapping(edges)

        # TODO: This is (amazingly) ugly in terms of OOP. Should refactor overlapping()
        if issubclass(qs.model, maintenance_models.Intervention):
            return qs.filter(target_id__in=[topo.pk for topo in overlapping])
        elif issubclass(qs.model, maintenance_models.Project):
            # Find all interventions overlapping those edges
            interventions = self._topology_filter(maintenance_models.Intervention.objects.existing()
                                                  .select_related('project')
                                                  .filter(project__in=qs),
                                                  edges)
            # Return only the projects concerned by the interventions
            projects = []
            for intervention in interventions:
                projects.append(intervention.project.pk)
            return qs.filter(pk__in=set(projects))

        else:
            assert issubclass(qs.model, Topology), "%s is not a Topology as expected" % qs.model
            return qs.filter(pk__in=[topo.pk for topo in overlapping])


class PathFilterSet(StructureRelatedFilterSet):
    length = OptionalRangeFilter(label=_('length'))
    name = CharFilter(label=_('Name'), lookup_expr='icontains')
    comments = CharFilter(label=_('Comments'), lookup_expr='icontains')

    class Meta(StructureRelatedFilterSet.Meta):
        model = Path
        fields = StructureRelatedFilterSet.Meta.fields + \
            ['valid', 'length', 'networks', 'usages', 'comfort', 'stake', 'draft', ]


class TrailFilterSet(StructureRelatedFilterSet):
    name = CharFilter(label=_('Name'), lookup_expr='icontains')
    departure = CharFilter(label=_('Departure'), lookup_expr='icontains')
    arrival = CharFilter(label=_('Arrival'), lookup_expr='icontains')
    comments = CharFilter(label=_('Comments'), lookup_expr='icontains')

    class Meta(StructureRelatedFilterSet.Meta):
        model = Trail
        fields = StructureRelatedFilterSet.Meta.fields + \
            ['name', 'departure', 'arrival', 'comments']


class TopologyFilterTrail(TopologyFilter):
    queryset = Trail.objects.existing()


if settings.TRAIL_MODEL_ENABLED:
    for filterset in (PathFilterSet, InfrastructureFilterSet, SignageFilterSet,
                      InterventionFilterSet, ProjectFilterSet):
        filterset.add_filters({
            'trail': TopologyFilterTrail(label=_('Trail'), required=False)
        })
