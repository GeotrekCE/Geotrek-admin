import operator
from datetime import date
from functools import reduce

from coreapi.document import Field
from django.conf import settings
from django.contrib.gis.db.models import Union
from django.db.models.query_utils import Q
from django.utils.translation import ugettext as _
from rest_framework.filters import BaseFilterBackend
from rest_framework_gis.filters import DistanceToPointFilter, InBBOXFilter

from geotrek.common.utils import intersecting
from geotrek.core.helpers import TopologyHelper
from geotrek.trekking.models import Trek
from geotrek.zoning.models import City, District


class GeotrekQueryParamsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset

    def get_schema_fields(self, view):
        field_language = Field(name='language', required=False,
                               description=_("Set language for translation. 'all' by default"),
                               example="fr")
        field_fields = Field(name='fields', required=False,
                             description=_("Limit required fields to increase performances. Ex : id,url,geometry"))
        field_omit = Field(name='omit', required=False,
                           description=_("Omit specified fields to increase performance. Ex: url,category"))
        return field_language, field_fields, field_omit


class GeotrekQueryParamsDimensionFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset

    def get_schema_fields(self, view):
        field_format = Field(name='format', required=False,
                             description=_("Set output format (json / geojson). JSON by default"),
                             example="geojson")
        return field_format,


class GeotrekInBBoxFilter(InBBOXFilter):
    """
    Override DRF gis InBBOXFilter with coreapi field descriptors
    """

    def get_schema_fields(self, view):
        field_in_bbox = Field(name=self.bbox_param, required=False,
                              description=_('Filter elements contained in bbox formatted like SW-lng,SW-lat,NE-lng,NE-lat'),
                              example='1.15,46.1,1.56,47.6')

        return field_in_bbox,


class GeotrekDistanceToPointFilter(DistanceToPointFilter):
    """
    Override DRF gis DistanceToPointFilter with coreapi field descriptors
    """

    def get_schema_fields(self, view):
        field_dist = Field(name=self.dist_param, required=False,
                           description=_('Max distance in meters between point and elements'),
                           type='number',
                           example='XXX')
        field_point = Field(name=self.point_param, required=False,
                            description=_('Reference point to compute distance LNG,LAT'),
                            example='1.2563,46.5214', )
        return field_dist, field_point


class GeotrekPublishedFilter(BaseFilterBackend):
    """
    Filter with published state in combination with language
    """

    def filter_queryset(self, request, queryset, view):
        qs = queryset
        language = request.GET.get('language', 'all')
        associated_published_fields = [f.name for f in qs.model._meta.get_fields() if f.name.startswith('published')]

        # if the model of the queryset published field is not translated
        if len(associated_published_fields) == 1:
            qs = qs.filter(published=True)
        elif len(associated_published_fields) > 1:
            # the published field of the queryset model is translated
            if language == 'all':
                # no language specified. Check for all.
                filters = list()
                for lang in settings.MODELTRANSLATION_LANGUAGES:
                    field_name = 'published_{}'.format(lang)
                    if field_name in associated_published_fields:
                        filters.append(Q(**{field_name: True}))
                if filters:
                    qs = qs.filter(reduce(operator.or_, filters))
            else:
                # one language is specified
                field_name = 'published_{}'.format(language)
                qs = qs.filter(Q(**{field_name: True}))

        return qs


class GeotrekSensitiveAreaFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        qs = queryset
        practices = request.GET.get('practices', '')
        if practices:
            qs = qs.filter(species__practices__id__in=practices.split(','))
        structure = request.GET.get('structure', '')
        if structure:
            qs = qs.filter(structure_id=structure)
        period = request.GET.get('period', '')
        if not period:
            qs = qs.filter(**{'species__period{:02}'.format(date.today().month): True})
        elif period == 'any':
            qs = qs.filter(reduce(operator.or_, (Q(**{'species__period{:02}'.format(m): True}) for m in range(1, 13))))
        elif period == 'ignore':
            pass
        else:
            months = [int(m) for m in period.split(',')]
            qs = qs.filter(reduce(operator.or_, (Q(**{'species__period{:02}'.format(m): True}) for m in months)))
        return qs.distinct()

    def get_schema_fields(self, view):
        field_period = Field(name='period', required=False,
                             description=_('Period of occupancy. Month numbers (1-12) separated by comas. any = occupied at any time in the year. ignore = occupied or not.'),
                             example='7,8 for july and august')
        field_practices = Field(name='practices', required=False,
                                description=_('Practices ids separated by comas.'),
                                example='1,3')
        field_structure = Field(name='structure', required=False,
                                description=_('Structure id.'),
                                example='5')
        return field_period, field_practices, field_structure


class GeotrekPOIFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        qs = queryset
        type = request.GET.get('type', None)
        if type is not None:
            qs = qs.filter(type=type)
        trek = request.GET.get('trek', None)
        if trek is not None:
            qs = TopologyHelper.overlapping(qs, Trek.objects.get(pk=trek))
        return qs

    def get_schema_fields(self, view):
        type = Field(name='type', required=False,
                     description=_("Limit to POIs that contains a specific POI Type"),
                     example=5)
        trek = Field(name='trek', required=False,
                     description=_("Id of a trek. It will show only the POIs related to this trek"),
                     example=970)
        return type, trek


class GeotrekTouristicContentFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        qs = queryset
        trek = request.GET.get('near_trek', None)
        if trek is not None:
            contents_intersecting = intersecting(qs.model, Trek.objects.get(pk=trek))
            # qs = qs.intersecting(contents_intersecting)  #FIXME: cannot intersect MultilingualQuerySet
            qs = contents_intersecting.order_by('id')
        return qs

    def get_schema_fields(self, view):
        near_trek = Field(name='near_trek', required=False,
                          description=_("Id of a trek. It will show only the touristics contents related to this trek"),
                          example=808)
        return near_trek,


class GeotrekTrekQueryParamsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        qs = queryset
        duration_min = request.GET.get('duration_min', None)
        if duration_min is not None:
            qs = qs.filter(duration__gte=duration_min)
        duration_max = request.GET.get('duration_max', None)
        if duration_max is not None:
            qs = qs.filter(duration__lte=duration_max)
        length_min = request.GET.get('length_min', None)
        if length_min is not None:
            qs = qs.filter(length__gte=length_min)
        length_max = request.GET.get('length_max', None)
        if length_max is not None:
            qs = qs.filter(length__lte=length_max)
        difficulty_min = request.GET.get('difficulty_min', None)
        if difficulty_min is not None:
            qs = qs.filter(difficulty__cirkwi_level__gte=difficulty_min)
        difficulty_max = request.GET.get('difficulty_max', None)
        if difficulty_max is not None:
            qs = qs.filter(difficulty__cirkwi_level__lte=difficulty_max)
        ascent_min = request.GET.get('ascent_min', None)
        if ascent_min is not None:
            qs = qs.filter(ascent__gte=ascent_min)
        ascent_max = request.GET.get('ascent_max', None)
        if ascent_max is not None:
            qs = qs.filter(ascent__lte=ascent_max)
        city = request.GET.get('city', None)
        if city is not None:
            cities_list = [int(c) for c in city.split(',')]
            union_geom = City.objects.filter(
                reduce(operator.or_, (Q(**{'code': c}) for c in cities_list))
            ).aggregate(Union('geom'))['geom__union']
            qs = qs.filter(geom__intersects=union_geom)
        district = request.GET.get('district', None)
        if district is not None:
            districts_list = [int(d) for d in district.split(',')]
            union_geom = District.objects.filter(
                reduce(operator.or_, (Q(**{'pk': d}) for d in districts_list))
            ).aggregate(Union('geom'))['geom__union']
            qs = qs.filter(geom__intersects=union_geom)
        structure = request.GET.get('structure', None)
        if structure is not None:
            qs = qs.filter(structure__pk=structure)
        accessibilities = request.GET.get('accessibility', None)
        if accessibilities is not None:
            list_accessibilities = [int(a) for a in accessibilities.split(',')]
            qs = qs.filter(accessibilities__in=list_accessibilities)
        themes = request.GET.get('theme', None)
        if themes is not None:
            list_themes = [int(t) for t in themes.split(',')]
            qs = qs.filter(themes__in=list_themes)
        portals = request.GET.get('portal', None)
        if portals is not None:
            list_portals = [int(p) for p in portals.split(',')]
            qs = qs.filter(portal__in=list_portals)
        route = request.GET.get('route', None)
        if route is not None:
            qs = qs.filter(route__pk=route)
        labels = request.GET.get('label', None)
        if labels is not None:
            list_labels = [int(label) for label in labels.split(',')]
            qs = qs.filter(portal__in=list_labels)
        q = request.GET.get('q', None)
        if q is not None:
            qs = qs.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
                | Q(description_teaser__icontains=q) | Q(ambiance__icontains=q)
            )
        return qs

    def get_schema_fields(self, view):
        field_duration_min = Field(
            name='duration_min', required=False,
            description=_('Set minimum duration for a trek'),
            example=2.5, type='integer'
        )
        field_duration_max = Field(
            name='duration_max', required=False,
            description=_('Set maximum duration for a trek'),
            example=7.5, type='integer'
        )
        field_length_min = Field(
            name='length_min', required=False,
            description=_('Set minimum length for a trek'),
            example=5500, type='integer'
        )
        field_length_max = Field(
            name='length_max', required=False,
            description=_('Set maximum length for a trek'),
            example=18000, type='integer'
        )
        field_difficulty_min = Field(
            name='difficulty_min', required=False,
            description=_('Set minimum difficulty for a trek. Difficulty usually goes from 1 (very easy) to 4 (difficult)'),
            example=3, type='integer'
        )
        field_difficulty_max = Field(
            name='difficulty_max', required=False,
            description=_('Set maximum difficulty for a trek. Difficulty usually goes from 1 (very easy) to 4 (difficult)'),
            example=4, type='integer'
        )
        field_ascent_min = Field(
            name='ascent_min', required=False,
            description=_('Set minimum ascent for a trek'),
            example=250, type='integer'
        )
        field_ascent_max = Field(
            name='ascent_max', required=False,
            description=_('Set maximum ascent for a trek'),
            example=1200, type='integer'
        )
        field_city = Field(
            name='city', required=False,
            description=_('Id of a city to filter by. Can be multiple cities split by a comma'),
            example='31006,31555,31017', type='string'
        )
        field_district = Field(
            name='district', required=False,
            description=_('Id of a district to filter by. Can be multiple districts split by a comma'),
            example='2273,2270', type='string'
        )
        field_structure = Field(
            name='structure', required=False,
            description=_('Id of a structure to filter by'),
            example=4, type='integer'
        )
        field_accessibilities = Field(
            name='accessibility', required=False,
            description=_('Id of the accessibilities to filter by, separated by commas'),
            example='1,2', type='string'
        )
        field_themes = Field(
            name='theme', required=False,
            description=_('Id of the themes to filter by, separated by commas'),
            example='9,14', type='string'
        )
        field_portals = Field(
            name='portal', required=False,
            description=_('Id of the portals to filter by, separated by commas'),
            example='3,7', type='string'
        )
        field_route = Field(
            name='route', required=False,
            description=_('Id of the type of route to filter by'),
            example='1', type='string'
        )
        field_label = Field(
            name='label', required=False,
            description=_('Id of the trek label to filter by, separated by commas'),
            example='1', type='string'
        )
        field_q = Field(
            name='q', required=False,
            description=_('Search field that returns treks contianing data matching the string'),
            example='query string', type='string'
        )
        return field_accessibilities, field_ascent_max, field_ascent_min, \
            field_city, field_difficulty_max, field_difficulty_min, \
            field_district, field_duration_max, field_duration_min, field_label, \
            field_length_max, field_length_min, field_portals, field_q, \
            field_route, field_structure, field_themes
