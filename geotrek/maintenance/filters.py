from django.forms.widgets import Select
from django.utils.translation import ugettext_lazy as _

from mapentity.filters import PolygonFilter, PythonPolygonFilter, YearFilter, YearBetweenFilter

from geotrek.core.models import Topology
from geotrek.land.filters import EdgeStructureRelatedFilterSet

from .models import Intervention, Project


class PolygonTopologyFilter(PolygonFilter):
    def filter(self, qs, value):
        if not value:
            return qs
        lookup = self.lookup_type
        inner_qs = Topology.objects.filter(**{'geom__%s' % lookup: value})
        return qs.filter(**{'%s__in' % self.name: inner_qs})


class InterventionYearSelect(Select):
    def render_options(self, *args, **kwargs):
        all_dates = Intervention.objects.existing().values_list('date', flat=True)
        all_years = list(reversed(sorted(set([d.year for d in all_dates]))))
        self.choices = list(enumerate([self.choices[0][1]] + all_years))
        return super(InterventionYearSelect, self).render_options(*args, **kwargs)


class InterventionFilter(EdgeStructureRelatedFilterSet):
    bbox = PolygonTopologyFilter(name='topology', lookup_type='intersects')
    year = YearFilter(name='date', widget=InterventionYearSelect, label=_(u"Year"))

    class Meta(EdgeStructureRelatedFilterSet.Meta):
        model = Intervention
        fields = EdgeStructureRelatedFilterSet.Meta.fields + [
            'status', 'type', 'stake', 'project'
        ]


class ProjectYearSelect(Select):
    def render_options(self, *args, **kwargs):
        all_years = []
        for p in Project.objects.existing():
            all_years.append(p.begin_year)
            all_years.append(p.end_year)
        all_years = list(reversed(sorted(set(all_years))))
        self.choices = list(enumerate([self.choices[0][1]] + all_years))
        return super(ProjectYearSelect, self).render_options(*args, **kwargs)


class ProjectFilter(EdgeStructureRelatedFilterSet):
    bbox = PythonPolygonFilter(name='geom')
    in_year = YearBetweenFilter(name=('begin_year', 'end_year'),
                                widget=ProjectYearSelect,
                                label=_(u"Year of activity"))

    class Meta(EdgeStructureRelatedFilterSet.Meta):
        model = Project
        fields = EdgeStructureRelatedFilterSet.Meta.fields
