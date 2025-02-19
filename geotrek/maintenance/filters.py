from django.db.models import Q
from django.conf import settings
from django.contrib.gis.geos import GeometryCollection
from django.utils.translation import gettext_lazy as _
from django.utils.text import format_lazy
from django_filters import ChoiceFilter, MultipleChoiceFilter, DateFromToRangeFilter, ModelMultipleChoiceFilter

from mapentity.filters import PolygonFilter, PythonPolygonFilter

from geotrek.altimetry.filters import AltimetryPointFilterSet
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.common.filters import OptionalRangeFilter, RightFilter
from geotrek.common.widgets import OneLineRangeWidget
from geotrek.zoning.filters import (IntersectionFilterCity, IntersectionFilterDistrict,
                                    IntersectionFilterRestrictedArea, IntersectionFilterRestrictedAreaType,
                                    ZoningFilterSet)
from geotrek.zoning.models import City, District, RestrictedArea, RestrictedAreaType

from .models import Intervention, Project, Contractor


class BboxInterventionFilterMixin:
    def filter(self, qs, value):
        if value:
            value = value.transform(settings.SRID, clone=True)
            return super().filter(qs, [value, ])
        else:
            return qs


class PolygonInterventionFilterMixin:
    def get_geom(self, value):
        return value

    def filter(self, qs, values):
        if not values:
            return qs
        geom_intersect = GeometryCollection([self.get_geom(value) for value in values])
        interventions = []
        for element in qs:
            if element.target:
                if not element.target.geom or element.target.geom.intersects(geom_intersect):
                    interventions.append(element.pk)
            elif element.target_type:
                interventions.append(element.pk)

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


class PolygonTopologyFilter(BboxInterventionFilterMixin, PolygonInterventionFilterMixin, PolygonFilter):
    pass


class ProjectIntersectionFilterCity(PolygonProjectFilterMixin, RightFilter):
    model = City


class ProjectIntersectionFilterDistrict(PolygonProjectFilterMixin, RightFilter):
    model = District


class ProjectIntersectionFilterRestrictedArea(PolygonProjectFilterMixin, RightFilter):
    model = RestrictedArea

    def get_queryset(self, request=None):
        qs = super().get_queryset(request)
        return qs.select_related('area_type')


class ProjectIntersectionFilterRestrictedAreaType(PolygonProjectFilterMixin, RightFilter):
    model = RestrictedAreaType

    def filter(self, qs, values):
        restricted_areas = RestrictedArea.objects.filter(area_type__in=values)
        if not restricted_areas and values:
            return qs.none()
        return super().filter(qs, list(restricted_areas)).distinct()


class AltimetryInterventionFilterSet(AltimetryPointFilterSet):
    length_3d = OptionalRangeFilter(field_name='length', label=_('length 3d'))
    ascent = OptionalRangeFilter(label=_('ascent'))
    descent = OptionalRangeFilter(label=_('descent'))
    slope = OptionalRangeFilter(label=_('slope'))


class CustomDateFromToRangeFilter(DateFromToRangeFilter):
    def __init__(self, *args, **kwargs):
        super(DateFromToRangeFilter, self).__init__(*args, **kwargs)
        self.field.fields[0].label = format_lazy('{min} {label}', min=_('min'), label=self.field.label)
        self.field.fields[1].label = format_lazy('{max} {label}', max=_('max'), label=self.field.label)


class InterventionFilterSet(AltimetryInterventionFilterSet, ZoningFilterSet, StructureRelatedFilterSet):
    ON_CHOICES = (('infrastructure', _("Infrastructure")), ('signage', _("Signage")), ('blade', _("Blade")),
                  ('topology', _("Path")), ('trek', _("Trek")), ('poi', _("POI")), ('service', _("Service")),
                  ('trail', _("Trail")), ('report', _("Report")))

    if 'geotrek.outdoor' in settings.INSTALLED_APPS:
        ON_CHOICES += (('course', _("Outdoor Course")), ('site', _("Outdoor Site")),)

    bbox = PolygonTopologyFilter(lookup_expr='intersects')
    begin_date = CustomDateFromToRangeFilter(widget=OneLineRangeWidget(attrs={'type': 'text', 'class': 'minmax-field', 'title': _('Filter by begin date range')},), label=_('begin date'))
    end_date = CustomDateFromToRangeFilter(widget=OneLineRangeWidget(attrs={'type': 'text', 'class': 'minmax-field', 'title': _('Filter by end date range')},), label=_('end date'))
    year = MultipleChoiceFilter(choices=lambda: Intervention.objects.year_choices(),
                                method='filter_year', label=_("Year"))
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
            'status', 'type', 'stake', 'subcontracting', 'project', 'contractors', 'on',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sorted 'ON_CHOICES' here to sort with user language.
        self.form.fields["on"].choices = sorted(self.ON_CHOICES, key=lambda modelname: modelname[1])

    def filter_year(self, qs, name, values):
        conditions = Q()
        for value in values:
            # Filter only with precise begin year
            conditions |= Q(begin_date__year=value, end_date__isnull=True)
            # Filter year between begin and end date
            conditions |= Q(begin_date__year__lte=value, end_date__year__gte=value)
        return qs.filter(conditions)


class ProjectFilterSet(StructureRelatedFilterSet):
    bbox = PythonPolygonFilter(field_name='geom')
    year = MultipleChoiceFilter(
        label=_("Year of activity"), method='filter_year',
        choices=lambda: Project.objects.year_choices()
    )
    city = ProjectIntersectionFilterCity(label=_('City'), lookup_expr='intersects', required=False)
    district = ProjectIntersectionFilterDistrict(label=_('District'), lookup_expr='intersects', required=False)
    area_type = ProjectIntersectionFilterRestrictedAreaType(label=_('Restricted area type'), lookup_expr='intersects', required=False)
    area = ProjectIntersectionFilterRestrictedArea(label=_('Restricted area'), lookup_expr='intersects', required=False)
    contractors = ModelMultipleChoiceFilter(label=_("Contractors"), queryset=Contractor.objects.all(), method='filter_contractors')

    class Meta(StructureRelatedFilterSet.Meta):
        model = Project
        fields = StructureRelatedFilterSet.Meta.fields + [
            'year', 'type', 'domain', 'contractors', 'project_owner',
            'project_manager', 'founders'
        ]

    def filter_contractors(self, qs, name, values):
        q = Q()
        if values:
            q |= Q(contractors__in=values)
            q |= Q(interventions__contractors__in=values)
        return qs.filter(q)

    def filter_year(self, qs, name, values):
        q = Q()
        for value in values:
            q |= Q(begin_year__lte=value, end_year__gte=value)
        return qs.filter(q)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields['year'].choices = Project.objects.year_choices()
