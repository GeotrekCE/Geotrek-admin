from django.db.models import Q
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django_filters import ChoiceFilter, MultipleChoiceFilter, FilterSet

from mapentity.filters import PolygonFilter, PythonPolygonFilter

from geotrek.altimetry.filters import AltimetryAllGeometriesFilterSet
from geotrek.core.models import Topology
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.common.filters import RightFilter
from geotrek.zoning.filters import (IntersectionFilterCity, IntersectionFilterDistrict,
                                    IntersectionFilterRestrictedArea, IntersectionFilterRestrictedAreaType,
                                    ZoningFilterSet)
from geotrek.zoning.models import City, District, RestrictedArea, RestrictedAreaType

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
        content_type_exclude = []
        if 'geotrek.signage' in settings.INSTALLED_APPS:
            blade_content_type = ContentType.objects.get_for_model(Blade)
            content_type_exclude.append(blade_content_type)
        if 'geotrek.outdoor' in settings.INSTALLED_APPS:
            site_content_type = ContentType.objects.get_for_model(Site)
            course_content_type = ContentType.objects.get_for_model(Course)
            content_type_exclude.append(site_content_type)
            content_type_exclude.append(course_content_type)
        topologies = []
        sites = []
        courses = []
        for value in values:
            topologies += Topology.objects.filter(**{'geom__%s' % lookup: self.get_geom(value)}).values_list('id', flat=True)

            if 'geotrek.outdoor' in settings.INSTALLED_APPS:
                sites += Site.objects.filter(**{'geom__%s' % lookup: self.get_geom(value)}).values_list('id', flat=True)
                courses += Course.objects.filter(**{'geom__%s' % lookup: self.get_geom(value)}).values_list('id', flat=True)
        topologies_intervention = Intervention.objects.existing().filter(target_id__in=topologies).exclude(
            target_type__in=content_type_exclude).distinct('pk').values_list('id', flat=True)

        interventions = list(topologies_intervention)
        if 'geotrek.signage' in settings.INSTALLED_APPS:
            blades = list(Blade.objects.filter(signage__in=topologies).values_list('id', flat=True))
            blades_intervention = Intervention.objects.existing().filter(target_id__in=blades,
                                                                         target_type=blade_content_type).values_list('id',
                                                                                                                     flat=True)
            interventions.extend(blades_intervention)
        if 'geotrek.outdoor' in settings.INSTALLED_APPS:
            sites_intervention = Intervention.objects.existing() \
                .filter(target_id__in=sites, target_type=site_content_type) \
                .values_list('id', flat=True)
            interventions.extend(sites_intervention)
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


class InterventionIntersectionFilterRestrictedAreaType(PolygonInterventionFilterMixin,
                                                       IntersectionFilterRestrictedAreaType):

    def get_geom(self, value):
        return value.geom

    def filter(self, qs, values):
        restricted_areas = RestrictedArea.objects.filter(area_type__in=values)
        if not restricted_areas and values:
            return qs.none()
        return super().filter(qs, list(restricted_areas))


class InterventionIntersectionFilterRestrictedArea(PolygonInterventionFilterMixin,
                                                   IntersectionFilterRestrictedArea):
    def get_geom(self, value):
        return value.geom


class InterventionIntersectionFilterCity(PolygonInterventionFilterMixin,
                                         IntersectionFilterCity):
    def get_geom(self, value):
        return value.geom


class InterventionIntersectionFilterDistrict(PolygonInterventionFilterMixin,
                                             IntersectionFilterDistrict):
    def get_geom(self, value):
        return value.geom


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


class ProjectIntersectionFilterRestrictedArea(PolygonInterventionFilterMixin, RightFilter):
    model = RestrictedArea

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookup_expr = 'intersects'
        self.lookup_queryset_in = 'interventions__in'

    def get_geom(self, value):
        return value.geom


class ProjectIntersectionFilterRestrictedAreaType(PolygonInterventionFilterMixin, RightFilter):
    model = RestrictedAreaType

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookup_expr = 'intersects'
        self.lookup_queryset_in = 'interventions__in'

    def filter(self, qs, values):
        restricted_areas = RestrictedArea.objects.filter(area_type__in=values)
        if not restricted_areas and values:
            return qs.none()
        return super().filter(qs, list(restricted_areas))

    def get_geom(self, value):
        return value.geom


class InterventionFilterSet(AltimetryAllGeometriesFilterSet, ZoningFilterSet, StructureRelatedFilterSet):
    ON_CHOICES = (('infrastructure', _("Infrastructure")), ('signage', _("Signage")), ('blade', _("Blade")),
                  ('topology', _("Path")), ('trek', _("Trek")), ('poi', _("POI")), ('service', _("Service")),
                  ('trail', _("Trail")))

    if 'geotrek.outdoor' in settings.INSTALLED_APPS:
        ON_CHOICES += (('course', _("Outdoor Course")), ('site', _("Outdoor Site")),)

    bbox = PolygonTopologyFilter(lookup_expr='intersects')
    year = MultipleChoiceFilter(choices=Intervention.objects.year_choices(),
                                field_name='date', lookup_expr='year', label=_("Year"))
    on = ChoiceFilter(field_name='target_type__model', choices=ON_CHOICES, label=_("On"), empty_label=_("On"))
    area_type = InterventionIntersectionFilterRestrictedAreaType(label=_('Restricted area type'), required=False,
                                                                 lookup_expr='intersects')
    area = InterventionIntersectionFilterRestrictedArea(label=_('Restricted area'), required=False,
                                                        lookup_expr='intersects')
    city = InterventionIntersectionFilterCity(label=_('City'), required=False, lookup_expr='intersects')
    district = InterventionIntersectionFilterDistrict(label=_('District'), required=False, lookup_expr='intersects')

    @classmethod
    def get_filters(cls):
        filters = super(FilterSet, cls).get_filters()
        del filters['length']
        return filters

    class Meta(StructureRelatedFilterSet.Meta):
        model = Intervention
        fields = StructureRelatedFilterSet.Meta.fields + [
            'status', 'type', 'stake', 'subcontracting', 'project', 'on',
        ]


class ProjectFilterSet(StructureRelatedFilterSet):
    bbox = PythonPolygonFilter(field_name='geom')
    year = MultipleChoiceFilter(
        label=_("Year of activity"), method='filter_year',
        choices=lambda: Project.objects.year_choices()  # Could change over time
    )
    city = ProjectIntersectionFilterCity(label=_('City'), required=False)
    district = ProjectIntersectionFilterDistrict(label=_('District'), required=False)
    area_type = ProjectIntersectionFilterRestrictedAreaType(label=_('Restricted area type'), required=False)
    area = ProjectIntersectionFilterRestrictedArea(label=_('Restricted area'), required=False)

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
