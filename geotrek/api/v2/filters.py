import operator
from datetime import date
from functools import reduce
import coreschema

from coreapi.document import Field
from django.conf import settings
from django.contrib.gis.db.models import Union
from django.db.models.query_utils import Q
from django.utils.translation import gettext as _
from rest_framework.filters import BaseFilterBackend
from rest_framework_gis.filters import DistanceToPointFilter, InBBOXFilter

from geotrek.common.utils import intersecting
from geotrek.core.models import Topology
from geotrek.trekking.models import Trek
from geotrek.zoning.models import City, District


class GeotrekQueryParamsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset

    def get_schema_fields(self, view):
        return (
            Field(
                name='language', required=False, location='query', schema=coreschema.String(
                    title=_("Language"),
                    description=_("Set language for translation. Default: all. Example: fr")
                )
            ), Field(
                name='fields', required=False, location='query', schema=coreschema.String(
                    title=_("Fields"),
                    description=_("Limit required fields to increase performances. Example: id,url,geometry")
                )
            ), Field(
                name='omit', required=False, location='query', schema=coreschema.String(
                    title=_("Omit"),
                    description=_("Omit specified fields to increase performance. Example: url,category")
                )
            ),
        )


class GeotrekQueryParamsDimensionFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset

    def get_schema_fields(self, view):
        return (
            Field(
                name='format', required=False, location='query', schema=coreschema.String(
                    title=_("Format"),
                    description=_("Set output format (json / geojson). Default: json. Example: geojson")
                )
            ),
        )


class GeotrekInBBoxFilter(InBBOXFilter):
    """
    Override DRF gis InBBOXFilter with coreapi field descriptors
    """

    def get_schema_fields(self, view):
        return (
            Field(
                name=self.bbox_param, required=False, location='query', schema=coreschema.String(
                    title=_("In bbox"),
                    description=_('Filter elements contained in bbox formatted like SW-lng,SW-lat,NE-lng,NE-lat.'
                                  'Example: 1.15,46.1,1.56,47.6')
                )
            ),
        )


class GeotrekDistanceToPointFilter(DistanceToPointFilter):
    """
    Override DRF gis DistanceToPointFilter with coreapi field descriptors
    """

    def get_schema_fields(self, view):
        return (
            Field(
                name=self.dist_param, required=False, location='query', schema=coreschema.Integer(
                    title=_("Distance"),
                    description=_('Max distance in meters between point and elements')
                )
            ), Field(
                name=self.point_param, required=False, location='query', schema=coreschema.String(
                    title=_("Point"),
                    description=_('Reference point to compute distance LNG,LAT. Example: 1.2563,46.5214'),
                )
            ),
        )


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
        return (
            Field(
                name='period', required=False, location='query', schema=coreschema.String(
                    title=_("Period"),
                    description=_('Period of occupancy. Month numbers (1-12) separated by comas.'
                                  ' any = occupied at any time in the year. ignore = occupied or not.'
                                  ' Example: 7,8 for july and august')
                )
            ), Field(
                name='practices', required=False, location='query', schema=coreschema.String(
                    title=_("Practices"),
                    description=_('Practices ids separated by comas. Example: 1,3')
                )
            ), Field(
                name='structure', required=False, location='query', schema=coreschema.Integer(
                    title=_("Structure"),
                    description=_('Structure id. Example: 5')
                )
            ),
        )


class GeotrekPOIFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        qs = queryset
        type = request.GET.get('type', None)
        if type is not None:
            qs = qs.filter(type=type)
        trek = request.GET.get('trek', None)
        if trek is not None:
            qs = Topology.overlapping(Trek.objects.get(pk=trek), qs)
        return qs

    def get_schema_fields(self, view):
        return (
            Field(
                name='type', required=False, location='query', schema=coreschema.Integer(
                    title=_("Type"),
                    description=_("Limit to POIs that contains a specific POI Type")
                )
            ), Field(
                name='trek', required=False, location='query', schema=coreschema.Integer(
                    title=_("Trek"),
                    description=_("Id of a trek. It will show only the POIs related to this trek")
                )
            ),
        )


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
        return (
            Field(
                name='near_trek', required=False, location='query', schema=coreschema.Integer(
                    title=_("Near trek"),
                    description=_("Id of a trek. It will show only the touristics contents related to this trek")
                )
            ),
        )


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
        practices = request.GET.get('practice', None)
        if practices is not None:
            list_practices = [int(p) for p in practices.split(',')]
            qs = qs.filter(practice__in=list_practices)
        return qs

    def get_schema_fields(self, view):
        return (
            Field(
                name='duration_min', required=False, location='query', schema=coreschema.Number(
                    title=_("Duration min"),
                    description=_('Set minimum duration for a trek')
                )
            ), Field(
                name='duration_max', required=False, location='query', schema=coreschema.Number(
                    title=_("Duration max"),
                    description=_('Set maximum duration for a trek')
                )
            ), Field(
                name='length_min', required=False, location='query', schema=coreschema.Integer(
                    title=_("Length min"),
                    description=_('Set minimum length for a trek')
                )
            ), Field(
                name='length_max', required=False, location='query', schema=coreschema.Integer(
                    title=_("Length max"),
                    description=_('Set maximum length for a trek')
                )
            ), Field(
                name='difficulty_min', required=False, location='query', schema=coreschema.Integer(
                    title=_("Difficulty min"),
                    description=_('Set minimum difficulty for a trek. Difficulty usually goes from 1 (very easy) to 4 (difficult)')
                )
            ), Field(
                name='difficulty_max', required=False, location='query', schema=coreschema.Integer(
                    title=_("Difficulty max"),
                    description=_('Set maximum difficulty for a trek. Difficulty usually goes from 1 (very easy) to 4 (difficult)')
                )
            ), Field(
                name='ascent_min', required=False, location='query', schema=coreschema.Integer(
                    title=_("Ascent min"),
                    description=_('Set minimum ascent for a trek')
                )
            ), Field(
                name='ascent_max', required=False, location='query', schema=coreschema.Integer(
                    title=_("Ascent max"),
                    description=_('Set maximum ascent for a trek')
                )
            ), Field(
                name='city', required=False, location='query', schema=coreschema.String(
                    title=_("City"),
                    description=_('Id of a city to filter by. Can be multiple cities split by a comma. Example: 31006,31555,31017')
                )
            ), Field(
                name='district', required=False, location='query', schema=coreschema.String(
                    title=_("District"),
                    description=_('Id of a district to filter by. Can be multiple districts split by a comma. Example: 2273,2270')
                )
            ), Field(
                name='structure', required=False, location='query', schema=coreschema.Integer(
                    title=_("Structure"),
                    description=_('Id of a structure to filter by')
                )
            ), Field(
                name='accessibility', required=False, location='query', schema=coreschema.String(
                    title=_("Accessibility"),
                    description=_('Id of the accessibilities to filter by, separated by commas. Example: 1,2')
                )
            ), Field(
                name='theme', required=False, location='query', schema=coreschema.String(
                    title=_("Theme"),
                    description=_('Id of the themes to filter by, separated by commas. Example: 9,14')
                )
            ), Field(
                name='portal', required=False, location='query', schema=coreschema.String(
                    title=_("Portal"),
                    description=_('Id of the portals to filter by, separated by commas. Example: 3,7')
                )
            ), Field(
                name='route', required=False, location='query', schema=coreschema.Integer(
                    title=_("Route"),
                    description=_('Id of the type of route to filter by')
                )
            ), Field(
                name='label', required=False, location='query', schema=coreschema.String(
                    title=_("Label"),
                    description=_('Id of the trek label to filter by, separated by commas')
                )
            ), Field(
                name='q', required=False, location='query', schema=coreschema.String(
                    title=_("Query string"),
                    description=_('Search field that returns treks containing data matching the string')
                )
            ), Field(
                name='practice', required=False, location='query', schema=coreschema.String(
                    title=_("Practice"),
                    description=_('Id of the trek practice to filter by, separated by commas')
                )
            ),
        )


class GeotrekSiteFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        q = request.GET.get('q', None)
        if q is not None:
            queryset = queryset.filter(name__icontains=q)
        return queryset

    def get_schema_fields(self, view):
        return (
            Field(
                name='q', required=False, location='query', schema=coreschema.String(
                    title=_("Query string"),
                    description=_('Search field that returns sites containing data matching the string')
                )
            ),
        )


class GeotrekRatingScaleFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        q = request.GET.get('q', None)
        if q is not None:
            queryset = queryset.filter(name__icontains=q)
        practice = request.GET.get('practice', None)
        if practice is not None:
            queryset = queryset.filter(practice__pk=practice)
        return queryset

    def get_schema_fields(self, view):
        return (
            Field(
                name='q', required=False, location='query', schema=coreschema.String(
                    title=_("Query string"),
                    description=_('Search field that returns rating scales containing data matching the string')
                )
            ), Field(
                name='practice', required=False, location='query', schema=coreschema.Integer(
                    title=_("Practice"),
                    description=_('Id of a practice to filter by')
                )
            ),
        )


class GeotrekRatingFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        q = request.GET.get('q', None)
        if q is not None:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q) | Q(scale__name__icontains=q)
            )
        scale = request.GET.get('scale', None)
        if scale is not None:
            queryset = queryset.filter(scale__pk=scale)
        return queryset

    def get_schema_fields(self, view):
        return (
            Field(
                name='q', required=False, location='query', schema=coreschema.String(
                    title=_("Query string"),
                    description=_('Search field that returns rating scales containing data matching the string')
                )
            ), Field(
                name='scale', required=False, location='query', schema=coreschema.Integer(
                    title=_("Rating scale"),
                    description=_('Id of a rating scale to filter by')
                )
            ),
        )
