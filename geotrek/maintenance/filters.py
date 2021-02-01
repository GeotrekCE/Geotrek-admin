from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django_filters import ChoiceFilter

from mapentity.filters import PolygonFilter, PythonPolygonFilter

from geotrek.core.models import Topology
from geotrek.common.filters import (
    StructureRelatedFilterSet, YearFilter, YearBetweenFilter)
from geotrek.common.filters import RightFilter
from geotrek.common.widgets import YearSelect
from geotrek.zoning.filters import ZoningFilterSet
from geotrek.zoning.models import City, District

from .models import Intervention, Project

if 'geotrek.signage' in settings.INSTALLED_APPS:
    from geotrek.signage.models import Blade


class InterventionYearTargetFilter(YearFilter):
    def do_filter(self, qs, year):
        interventions = Intervention.objects.filter(date__year=year).values_list('target_id', flat=True)
        return qs.filter(**{
            'id__in': interventions
        }).distinct()


class PolygonInterventionFilterMixin(object):
    def get_geom(self, value):
        return value

    def filter(self, qs, value):
        if not value:
            return qs
        lookup = self.lookup_expr

        blade_content_type = ContentType.objects.get_for_model(Blade)
        topologies = list(Topology.objects.filter(**{'geom__%s' % lookup: self.get_geom(value)}).values_list('id', flat=True))
        topologies_intervention = Intervention.objects.existing().filter(target_id__in=topologies).exclude(
            target_type=blade_content_type).distinct('pk').values_list('id', flat=True)

        interventions = list(topologies_intervention)
        if 'geotrek.signage' in settings.INSTALLED_APPS:
            blades = list(Blade.objects.filter(signage__in=topologies).values_list('id', flat=True))
            blades_intervention = Intervention.objects.existing().filter(target_id__in=blades,
                                                                         target_type=blade_content_type).values_list('id',
                                                                                                                     flat=True)
            interventions.extend(blades_intervention)
        if hasattr(self, 'lookup_queryset_in'):
            lookup_queryset = self.lookup_queryset_in
        else:
            lookup_queryset = 'pk__in'
        qs = qs.filter(**{'%s' % lookup_queryset: interventions})
        return qs


class PolygonTopologyFilter(PolygonInterventionFilterMixin, PolygonFilter):
    pass


class ProjectIntersectionFilterCity(PolygonInterventionFilterMixin, RightFilter):
    model = City

    def __init__(self, *args, **kwargs):
        super(ProjectIntersectionFilterCity, self).__init__(*args, **kwargs)
        self.lookup_expr = 'intersects'
        self.lookup_queryset_in = 'interventions__in'

    def get_geom(self, value):
        return value.geom


class ProjectIntersectionFilterDistrict(PolygonInterventionFilterMixin, RightFilter):
    model = District

    def __init__(self, *args, **kwargs):
        super(ProjectIntersectionFilterDistrict, self).__init__(*args, **kwargs)
        self.lookup_expr = 'intersects'
        self.lookup_queryset_in = 'interventions__in'

    def get_geom(self, value):
        return value.geom


class InterventionYearSelect(YearSelect):
    label = _("Year")

    def get_years(self):
        return Intervention.objects.all_years()


class InterventionFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    ON_CHOICES = (('infrastructure', _("Infrastructure")), ('signage', _("Signage")), ('blade', _("Blade")),
                  ('topology', _("Path")), ('trek', _("Trek")), ('poi', _("POI")), ('service', _("Service")),
                  ('trail', _("Trail")))
    bbox = PolygonTopologyFilter(lookup_expr='intersects')
    year = YearFilter(field_name='date',
                      widget=InterventionYearSelect,
                      label=_("Year"))
    on = ChoiceFilter(field_name='target_type__model', choices=ON_CHOICES, label=_("On"), empty_label=_("On"))

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
    city = ProjectIntersectionFilterCity(label=_('City'), required=False)
    district = ProjectIntersectionFilterDistrict(label=_('District'), required=False)

    class Meta(StructureRelatedFilterSet.Meta):
        model = Project
        fields = StructureRelatedFilterSet.Meta.fields + [
            'in_year', 'type', 'domain', 'contractors', 'project_owner',
            'project_manager', 'founders'
        ]
