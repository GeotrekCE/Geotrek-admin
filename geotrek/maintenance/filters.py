from django.db.models import Q
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django_filters import ChoiceFilter, MultipleChoiceFilter

from mapentity.filters import PolygonFilter, PythonPolygonFilter

from geotrek.altimetry.filters import AltimetryPointFilterSet
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.common.filters import OptionalRangeFilter, RightFilter
from geotrek.feedback.models import Report
from geotrek.zoning.filters import (IntersectionFilterCity, IntersectionFilterDistrict,
                                    IntersectionFilterRestrictedArea, IntersectionFilterRestrictedAreaType,
                                    ZoningFilterSet)
from geotrek.zoning.models import City, District, RestrictedArea, RestrictedAreaType

from .models import Intervention, Project
from geotrek.core.models import Topology

if 'geotrek.signage' in settings.INSTALLED_APPS:
    from geotrek.signage.models import Blade, Signage

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

        if 'geotrek.signage' in settings.INSTALLED_APPS:
            blade_content_type = ContentType.objects.get_for_model(Blade)
        signages = []
        target_types = qs.values_list('target_type', flat=True).exclude(target_type=blade_content_type)
        interventions = []
        for target_type in target_types:
            model = ContentType.objects.get(pk=target_type).model_class()
            elements_in_bbox = []
            for value in values:
                elements_in_bbox.extend(
                    model.objects.filter(**{'geom__%s' % self.lookup_expr: self.get_geom(value)}).values_list('id', flat=True)
                )
            if 'geotrek.outdoor' in settings.INSTALLED_APPS and issubclass(model, Site) or issubclass(model, Course):
                interventions.extend(qs.values_list('id', flat=True).filter(target_type=target_type).exclude(
                    target_id__in=model.objects.values_list('id', flat=True)
                ))
            if 'geotrek.feedback' in settings.INSTALLED_APPS and issubclass(model, Report):
                interventions.extend(qs.values_list('id', flat=True).filter(target_type=target_type).exclude(
                    target_id__in=model.objects.values_list('id', flat=True)))
            if 'geotrek.signage' in settings.INSTALLED_APPS and issubclass(model, Topology) or issubclass(model, Signage):
                signages = elements_in_bbox
            interventions += qs.values_list('id', flat=True).filter(target_type=target_type,
                                                                    target_id__in=elements_in_bbox)

        if 'geotrek.signage' in settings.INSTALLED_APPS:
            blades = list(Blade.objects.filter(signage__in=signages).values_list('id', flat=True))

            blades_intervention = Intervention.objects.existing().filter(target_id__in=blades,
                                                                         target_type=blade_content_type).values_list('id',
                                                                                                                     flat=True)
            interventions.extend(blades_intervention)
        qs = qs.filter(pk__in=interventions).existing()
        return qs


class PolygonProjectFilterMixin(PolygonInterventionFilterMixin):
    def get_geom(self, value):
        return value.geom

    def filter(self, qs, values):
        if not values:
            return qs
        interventions = Intervention.objects.all()
        return qs.filter(interventions__in=super().filter(interventions, values).values_list('id', flat=True))


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


class ProjectIntersectionFilterCity(PolygonProjectFilterMixin, RightFilter):
    model = City


class ProjectIntersectionFilterDistrict(PolygonProjectFilterMixin, RightFilter):
    model = District


class ProjectIntersectionFilterRestrictedArea(PolygonProjectFilterMixin, RightFilter):
    model = RestrictedArea


class ProjectIntersectionFilterRestrictedAreaType(PolygonProjectFilterMixin, RightFilter):
    model = RestrictedAreaType

    def filter(self, qs, values):
        restricted_areas = RestrictedArea.objects.filter(area_type__in=values)
        if not restricted_areas and values:
            return qs.none()
        return super().filter(qs, list(restricted_areas))


class AltimetryInterventionFilterSet(AltimetryPointFilterSet):
    length_3d = OptionalRangeFilter(field_name='length', label=_('length 3d'))
    ascent = OptionalRangeFilter(label=_('ascent'))
    descent = OptionalRangeFilter(label=_('descent'))
    slope = OptionalRangeFilter(label=_('slope'))


class InterventionFilterSet(AltimetryInterventionFilterSet, ZoningFilterSet, StructureRelatedFilterSet):
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
    city = ProjectIntersectionFilterCity(label=_('City'), lookup_expr='intersects', required=False)
    district = ProjectIntersectionFilterDistrict(label=_('District'), lookup_expr='intersects', required=False)
    area_type = ProjectIntersectionFilterRestrictedAreaType(label=_('Restricted area type'), lookup_expr='intersects', required=False)
    area = ProjectIntersectionFilterRestrictedArea(label=_('Restricted area'), lookup_expr='intersects', required=False)

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
