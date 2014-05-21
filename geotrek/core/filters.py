# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django_filters import CharFilter, ModelChoiceFilter

from .models import Topology, Path, Trail

from geotrek.common.filters import OptionalRangeFilter, StructureRelatedFilterSet


class TopologyFilter(ModelChoiceFilter):

    model = None
    queryset = None

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', self.get_queryset())
        super(TopologyFilter, self).__init__(*args, **kwargs)
        self.field.widget.attrs['class'] = self.field.widget.attrs.get('class', '') + ' topology-filter'

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        return self.model.objects.all()

    def filter(self, qs, value):
        """Overrides parent filter() method completely.
        """
        if not value:
            return qs
        if issubclass(value.__class__, Topology):
            edges = Topology.objects.filter(pk=value.pk)
        else:
            edges = self.value_to_edges(value)
        return TopologyFilter._topology_filter(qs, edges)

    def value_to_edges(self, value):
        """
        For an instance of this filter model, returns a Topology queryset.
        """
        raise NotImplementedError

    @staticmethod
    def _topology_filter(qs, edges):
        """
        This piece of code should be rewritten nicely with managers : TODO !
        """
        import geotrek.maintenance as maintenance

        overlapping = Topology.overlapping(edges)

        # In case, we filter on paths
        if qs.model == Path:
            paths = []
            for o in overlapping:
                paths.extend(o.paths.all())
            return qs.filter(pk__in=[path.pk for path in set(paths)])

        # TODO: This is (amazingly) ugly in terms of OOP. Should refactor overlapping()
        elif issubclass(qs.model, maintenance.models.Intervention):
            return qs.filter(topology__in=[topo.pk for topo in overlapping])
        elif issubclass(qs.model, maintenance.models.Project):
            # Find all interventions overlapping those edges
            interventions = filter(maintenance.models.Intervention.objects.existing()
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
    name = CharFilter(label=_('Name'), lookup_type='icontains')
    comments = CharFilter(label=_('Comments'), lookup_type='icontains')

    class Meta(StructureRelatedFilterSet.Meta):
        model = Path
        fields = StructureRelatedFilterSet.Meta.fields + [
                    'valid', 'length', 'networks']


class TrailFilterSet(StructureRelatedFilterSet):
    name = CharFilter(label=_('Name'), lookup_type='icontains')
    departure = CharFilter(label=_('Departure'), lookup_type='icontains')
    arrival = CharFilter(label=_('Arrival'), lookup_type='icontains')
    comments = CharFilter(label=_('Comments'), lookup_type='icontains')

    class Meta(StructureRelatedFilterSet.Meta):
        model = Trail
        fields = StructureRelatedFilterSet.Meta.fields + [
                    'name', 'departure', 'arrival', 'comments']
