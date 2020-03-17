from django.utils.translation import ugettext_lazy as _
from django_filters import ChoiceFilter

from mapentity.filters import PolygonFilter, PythonPolygonFilter

from geotrek.core.models import Topology
from geotrek.common.filters import (
    StructureRelatedFilterSet, YearFilter, YearBetweenFilter)
from geotrek.common.widgets import YearSelect

from .models import Intervention, Project


class PolygonTopologyFilter(PolygonFilter):
    def filter(self, qs, value):
        print(qs.filter(signages__name="test"))
        if not value:
            return qs
        lookup = self.lookup_expr
        inner_qs = Topology.objects.filter(**{'geom__%s' % lookup: value})
        print(inner_qs)
        print({'infrastructures__%s__in' % self.field_name: inner_qs,
               'signages__%s__in' % self.field_name: inner_qs})
        qs = qs.filter(**{'infrastructures__%s__in' % self.field_name: inner_qs,
                          'signages__%s__in' % self.field_name: inner_qs})
        print(qs)
        return qs


class InterventionYearSelect(YearSelect):
    label = _("Year")

    def get_years(self):
        return Intervention.objects.all_years()


class InterventionFilterSet(StructureRelatedFilterSet):
    ON_CHOICES = (('INFRASTRUCTURE', _("Infrastructure")), ('SIGNAGE', _("Signage")))
    bbox = PolygonTopologyFilter(field_name='topo_object', lookup_expr='intersects')
    year = YearFilter(field_name='date',
                      widget=InterventionYearSelect,
                      label=_("Year"))
    on = ChoiceFilter(field_name='infrastructures__topo_object__kind', choices=ON_CHOICES, label=_("On"), empty_label=_("On"))

    class Meta(StructureRelatedFilterSet.Meta):
        model = Intervention
        fields = StructureRelatedFilterSet.Meta.fields + [
            'status', 'type', 'stake', 'subcontracting', 'project', 'on',
        ]


class ProjectYearSelect(YearSelect):
    label = _("Year of activity")

    def get_years(self):
        return Project.objects.all_years()


class ProjectFilterSet(StructureRelatedFilterSet):
    bbox = PythonPolygonFilter(field_name='geom')
    in_year = YearBetweenFilter(field_name=('begin_year', 'end_year'),
                                widget=ProjectYearSelect,
                                label=_("Year of activity"))

    class Meta(StructureRelatedFilterSet.Meta):
        model = Project
        fields = StructureRelatedFilterSet.Meta.fields + [
            'in_year', 'type', 'domain', 'contractors', 'project_owner',
            'project_manager', 'founders'
        ]
