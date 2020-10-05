from datetime import date
import operator
from functools import reduce

from coreapi.document import Field
from django.conf import settings
from django.db.models.query_utils import Q
from django.contrib.gis.db.models import Union
from django.utils.translation import ugettext as _
from rest_framework.filters import BaseFilterBackend
from rest_framework_gis.filters import InBBOXFilter, DistanceToPointFilter

from geotrek.zoning.models import City, District


class GeotrekQueryParamsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset

    def get_schema_fields(self, view):
        field_dim = Field(name='dim', required=False,
                          description=_('Set geometry dimension (2 by default for 2D, 3 for 3D)'),
                          example=3, type='integer')
        field_language = Field(name='language', required=False,
                               description=_("Set language for translation. 'all' by default"),
                               example="fr")
        field_format = Field(name='format', required=False,
                             description=_("Set output format (json / geojson). JSON by default"),
                             example="geojson")
        field_fields = Field(name='fields', required=False,
                             description=_("Limit required fields to increase performances. Ex : id,url,geometry"))
        field_omit = Field(name='omit', required=False,
                           description=_("Omit specified fields to increase performance. Ex: url,category"))
        return field_dim, field_language, field_format, field_fields, field_omit


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
        if not hasattr(queryset.model, 'published'):
            return queryset
        qs = queryset
        published = request.GET.get('published', 'true')

        if published.lower() == 'true':
            published = True
        elif published.lower() == 'false':
            published = False
        else:
            published = None
        if published is not None:
            language = request.GET.get('language', 'all')

            if published:
                # if language, check language published. Else, if true one language must me published, if false none
                if language == 'all':
                    filters = list()
                    for lang in settings.MODELTRANSLATION_LANGUAGES:
                        filters.append(Q(**{'published_{}'.format(lang): published}))

                    qs = qs.filter(reduce(operator.or_, filters))

                else:
                    qs = qs.filter(**{'published_{}'.format(language): published})
            else:
                if language == 'all':
                    filters = {}
                    for lang in settings.MODELTRANSLATION_LANGUAGES:
                        filters.update({'published_{}'.format(lang): False})

                    qs = qs.filter(**filters)

                else:
                    qs = qs.filter(**{'published_{}'.format(language): published})
        return qs

    def get_schema_fields(self, view):
        field_published = Field(name='published', required=False,
                                description=_('Publication state. If language specified, only language published are filterted. true/false/all. true by default.'),
                                type='boolean',
                                example='true')
        return field_published,


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
        accessibilities = request.GET.get('accessibilities', None)
        if accessibilities is not None:
            list_accessibilities = [int(a) for a in accessibilities.split(',')]
            qs = qs.filter(accessibilities__in=list_accessibilities)
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
            description=_('Code (pk) of a city to filter by. Can be multiple cities split by a comma'),
            example='31006,31555,31017', type='string'
        )
        field_district = Field(
            name='district', required=False,
            description=_('Pk of a district to filter by. Can be multiple districts split by a comma'),
            example='2273,2270', type='string'
        )
        field_structure = Field(
            name='structure', required=False,
            description=_('Pk of a structure to filter by'),
            example=4, type='integer'
        )
        field_accessibilities = Field(
            name='accessibilities', required=False,
            description=_('Pk a the accessibilities to filter by, separated by commas'),
            example='1,2', type='string'
        )
        return field_duration_min, field_duration_max, field_length_min,\
            field_length_max, field_difficulty_min, field_difficulty_max, \
            field_ascent_min, field_ascent_max, field_city, field_district, \
            field_structure, field_accessibilities
