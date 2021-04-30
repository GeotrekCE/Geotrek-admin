from django.db.models import Q
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django_filters import ChoiceFilter, MultipleChoiceFilter

from mapentity.filters import PolygonFilter

from geotrek.core.models import Topology
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.common.filters import RightFilter
from geotrek.zoning.filters import ZoningFilterSet
from geotrek.zoning.models import City, District

from .models import Intervention, Project

if 'geotrek.signage' in settings.INSTALLED_APPS:
    from geotrek.signage.models import Blade

if 'geotrek.outdoor' in settings.INSTALLED_APPS:
    from geotrek.outdoor.models import Site, Course


class PolygonInterventionFilterMixin:
    def get_geom(self, value):
        return value

    def filter(self, qs, values):
        if not values:
            return qs
        if not isinstance(values, list):
            values = [values]

        lookup = self.lookup_expr

        if 'geotrek.signage' in settings.INSTALLED_APPS:
            blade_content_type = ContentType.objects.get_for_model(Blade)
        if 'geotrek.outdoor' in settings.INSTALLED_APPS:
            site_content_type = ContentType.objects.get_for_model(Site)
            course_content_type = ContentType.objects.get_for_model(Course)

        topologies = []
        for value in values:
            topologies += Topology.objects.filter(**{'geom__%s' % lookup: self.get_geom(value)}).values_list('id', flat=True)
        topologies_intervention = Intervention.objects.existing().filter(target_id__in=topologies).exclude(
            target_type=blade_content_type).distinct('pk').values_list('id', flat=True)

        interventions = list(topologies_intervention)
        if 'geotrek.signage' in settings.INSTALLED_APPS:
            blades = list(Blade.objects.filter(signage__in=topologies).values_list('id', flat=True))
            blades_intervention = Intervention.objects.existing().filter(target_id__in=blades,
                                                                         target_type=blade_content_type).values_list('id',
                                                                                                                     flat=True)
            interventions.extend(blades_intervention)
        if 'geotrek.outdoor' in settings.INSTALLED_APPS:
            sites = list(Site.objects.filter(**{'geom__%s' % lookup: self.get_geom(value)}).values_list('id', flat=True))
            sites_intervention = Intervention.objects.existing() \
                .filter(target_id__in=sites, target_type=site_content_type) \
                .values_list('id', flat=True)
            interventions.extend(sites_intervention)
            courses = list(Course.objects.filter(**{'geom__%s' % lookup: self.get_geom(value)}).values_list('id', flat=True))
            courses_intervention = Intervention.objects.existing() \
                .filter(target_id__in=courses, target_type=course_content_type) \
                .values_list('id', flat=True)
            interventions.extend(courses_intervention)
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
        super().__init__(*args, **kwargs)
        self.lookup_expr = 'intersects'
        self.lookup_queryset_in = 'interventions__in'

    def get_geom(self, value):
        return value.geom


class ProjectIntersectionFilterDistrict(PolygonInterventionFilterMixin, RightFilter):
    model = District

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookup_expr = 'intersects'
        self.lookup_queryset_in = 'interventions__in'

    def get_geom(self, value):
        return value.geom


class InterventionFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    ON_CHOICES = (('infrastructure', _("Infrastructure")), ('signage', _("Signage")), ('blade', _("Blade")),
                  ('topology', _("Path")), ('trek', _("Trek")), ('poi', _("POI")), ('service', _("Service")),
                  ('trail', _("Trail")))
    bbox = PolygonTopologyFilter(lookup_expr='intersects')
    year = MultipleChoiceFilter(choices=Intervention.objects.year_choices(),
                                field_name='date', lookup_expr='year', label=_("Year"))
    on = ChoiceFilter(field_name='target_type__model', choices=ON_CHOICES, label=_("On"), empty_label=_("On"))

    class Meta(StructureRelatedFilterSet.Meta):
        model = Intervention
        fields = StructureRelatedFilterSet.Meta.fields + [
            'status', 'type', 'stake', 'subcontracting', 'project', 'on',
        ]


class ProjectFilterSet(StructureRelatedFilterSet):
    year = MultipleChoiceFilter(
        label=_("Year of activity"), method='filter_year',
        choices=lambda: Project.objects.year_choices()  # Could change over time
    )
    city = ProjectIntersectionFilterCity(label=_('City'), required=False)
    district = ProjectIntersectionFilterDistrict(label=_('District'), required=False)

    class Meta(StructureRelatedFilterSet.Meta):
        model = Project
        fields = StructureRelatedFilterSet.Meta.fields + [
            'year', 'type', 'domain', 'contractors', 'project_owner',
            'project_manager', 'founders'
        ]

    def filter_year(self, qs, name, values):
        q = Q()
        for value in values:
            q |= Q(begin_year__lte=value, end_year__gte=value)
        return qs.filter(q)
