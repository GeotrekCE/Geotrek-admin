from datetime import date, datetime
from distutils.util import strtobool

from django.conf import settings
from django.contrib.gis.db.models import Collect
from django.db.models import Exists, Model, OuterRef
from django.db.models.query_utils import Q
from django.utils.translation import gettext_lazy as _
from django_filters import ModelMultipleChoiceFilter
from django_filters import rest_framework as filters
from django_filters.widgets import CSVWidget
from modeltranslation.utils import build_localized_fieldname
from rest_framework.filters import BaseFilterBackend
from rest_framework_gis.filters import DistanceToPointFilter, InBBOXFilter

from geotrek.flatpages.models import FlatPage, MenuItem
from geotrek.tourism.models import (
    TouristicContent,
    TouristicContentType,
    TouristicEvent,
    TouristicEventOrganizer,
    TouristicEventPlace,
    TouristicEventType,
)
from geotrek.trekking.models import POI, ServiceType, Trek
from geotrek.zoning.models import City, District

if "geotrek.outdoor" in settings.INSTALLED_APPS:
    from geotrek.outdoor.models import Course, Site


def get_published_filter_expression(model: type[Model], language: str | None = None):
    """Given a model with a `published` field and a language string
    this function returns a query expression to filter on.

    `language` parameter is expected to be one of the modeltranslation's defined language or "all".
    """
    associated_published_fields = [
        f.name for f in model._meta.get_fields() if f.name.startswith("published")
    ]
    if len(associated_published_fields) == 1:
        # The model's published field is not translated
        return Q(published=True)
    elif len(associated_published_fields) > 1:
        # The published field is translated
        if not language or language == "all":
            # no language specified. Check for all.
            q = Q()
            for lang in settings.MODELTRANSLATION_LANGUAGES:
                field_name = build_localized_fieldname("published", lang)
                if field_name in associated_published_fields:
                    q |= Q(**{field_name: True})
            return q
        else:
            # one language is specified
            field_name = build_localized_fieldname("published", language)
            return Q(**{field_name: True})


class GeotrekQueryParamsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        ids = request.GET.get("ids")
        if ids:
            queryset = queryset.filter(pk__in=ids.split(","))
        return queryset

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "language",
                "required": False,
                "in": "query",
                "description": _(
                    "Set language for translation. Can be all or a two-letters language code."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "fields",
                "required": False,
                "in": "query",
                "description": _(
                    "Limit required fields to increase performances. Example: id,url,geometry."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "omit",
                "required": False,
                "in": "query",
                "description": _(
                    "Omit specified fields to increase performance. Example: url,category."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "ids",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more object id, comma-separated."),
                "schema": {"type": "string"},
            },
        ]


class GeotrekQueryParamsDimensionFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "format",
                "required": False,
                "in": "query",
                "description": _(
                    "Set output format (json / geojson). Default: json. Example: geojson."
                ),
                "schema": {"type": "string"},
            },
        ]


class GeotrekInBBoxFilter(InBBOXFilter):
    """
    Override DRF gis InBBOXFilter with spectacular field descriptors
    """

    def get_filter_bbox(self, request):
        """Transform bbox to internal SRID to get working"""
        bbox = super().get_filter_bbox(request)
        if bbox:
            bbox.srid = 4326
            bbox.transform(settings.SRID)
        return bbox

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": self.bbox_param,
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by a bounding box formatted like W-lng,S-lat,E-lng,N-lat (WGS84)."
                    "Example: 1.15,46.1,1.56,47.6."
                ),
                "schema": {"type": "string"},
            },
        ]


class GeotrekDistanceToPointFilter(DistanceToPointFilter):
    """
    Override DRF gis DistanceToPointFilter with spectacular field descriptors
    """

    def get_filter_point(self, request, **kwargs):
        point = super().get_filter_point(request, **kwargs)
        if point:
            point.srid = 4326
            point.transform(settings.SRID)
        return point

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": self.dist_param,
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by maximum distance in meters between a point and elements."
                ),
                "schema": {"type": "integer"},
            },
            {
                "name": self.point_param,
                "required": False,
                "in": "query",
                "description": _(
                    "Reference point to compute distance (WGS84). Example: lng,lat."
                ),
                "schema": {"type": "string"},
            },
        ]


class GeotrekPublishedFilter(BaseFilterBackend):
    """Filter with published state in combination with language"""

    def filter_queryset(self, request, queryset, view):
        qs = queryset
        language = request.GET.get("language", "all")
        expr = get_published_filter_expression(qs.model, language)
        if expr:
            qs = qs.filter(expr)
        return qs


class GeotrekSensitiveAreaFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        qs = queryset
        practices = request.GET.get("practices")
        if practices:
            qs = qs.filter(species__practices__id__in=practices.split(","))
        structures = request.GET.get("structures")
        if structures:
            qs = qs.filter(structure__in=structures.split(","))
        period = request.GET.get("period")
        if not period:
            qs = qs.filter(**{f"species__period{date.today().month:02}": True})
        elif period == "any":
            q = Q()
            for m in range(1, 13):
                q |= Q(**{f"species__period{m:02}": True})
            qs = qs.filter(q)
        elif period == "ignore":
            pass
        else:
            q = Q()
            for m in [int(m) for m in period.split(",")]:
                q |= Q(**{f"species__period{m:02}": True})
            qs = qs.filter(q)
        trek_id = request.GET.get("trek")
        if trek_id:
            qs = _filter_near(
                base_model=qs.model, queryset=qs, target_model=Trek, target_pk=trek_id
            )
        return qs.distinct()

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "period",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by period of occupancy. Month numbers (1-12), comma-separated."
                    " any = occupied at any time in the year. ignore = occupied or not."
                    " Example: 7,8 for july and august."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "practices",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more practice id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "structures",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or more structure id, comma-separated."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "trek",
                "required": False,
                "in": "query",
                "description": _("(deprecated) replaced by '%(field)s'.")
                % {"field": "near_trek"},
                "schema": {"type": "integer"},
            },
        ]


class GeotrekPOIFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        qs = queryset
        types = request.GET.get("types", None)
        if types is not None:
            qs = qs.filter(type__in=types.split(","))
        trek = request.GET.get("trek", None)
        if trek is not None:
            qs = _filter_near(
                base_model=qs.model, queryset=qs, target_model=Trek, target_pk=trek
            )
        sites = request.GET.get("sites", None)
        if sites is not None:
            qs = qs.filter(pk__in=self.get_pois_to_filter_outdoor_objects(Site, sites))
        courses = request.GET.get("courses", None)
        if courses is not None:
            qs = qs.filter(
                pk__in=self.get_pois_to_filter_outdoor_objects(Course, courses)
            )
        return qs

    def get_pois_to_filter_outdoor_objects(self, model, elems):
        list_pois = POI.objects.none()
        objects_outdoor = model.objects.filter(pk__in=elems.split(","))
        collected_geom = objects_outdoor.aggregate(collected_geom=Collect("geom"))[
            "collected_geom"
        ]
        if collected_geom:
            list_pois = (
                POI.objects.existing()
                .filter(
                    geom__dwithin=(collected_geom, settings.OUTDOOR_INTERSECTION_MARGIN)
                )
                .exclude(
                    pk__in=objects_outdoor.values_list(
                        "pois_excluded", flat=True
                    ).filter(pois_excluded__isnull=False)
                )
            )
        return list_pois.distinct()

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "types",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more type id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "trek",
                "required": False,
                "in": "query",
                "description": _("(deprecated) replaced by '%(field)s'.")
                % {"field": "near_trek"},
                "schema": {"type": "integer"},
            },
            {
                "name": "sites",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or multiple site id. It will show only the POIs related to this outdoor site. If multiple sites, they should be separated by commas."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "courses",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or multiple course id. It will show only the POIs related to this outdoor course. If multiple courses, they should be separated by commas."
                ),
                "schema": {"type": "string"},
            },
        ]


def _filter_near(base_model, target_model, target_pk, queryset):
    """Filter the queryset of base_model objects by keeping only the objects near the target.

    The function uses the model properties to achieve the filtering. For instance it would find and use the `target_trek.pois` property to filter
    q POI queryset near a target trek.

    Return an empty queryset if the target does not exist.
    """

    def pluralize(name):
        return name + "s"

    try:
        target = target_model.objects.get(pk=target_pk)
    except target_model.DoesNotExist:
        return queryset.none()
    prop_name = getattr(
        base_model, "related_near_objects_property_name", None
    ) or pluralize(base_model._meta.model_name)
    prop = getattr(target_model, prop_name)
    return prop.fget(target, queryset)


class NearbyContentFilter(BaseFilterBackend):
    def filter_queryset(self, request, qs, view):
        near_touristicevent = request.GET.get("near_touristicevent")
        if near_touristicevent:
            qs = _filter_near(
                base_model=qs.model,
                queryset=qs,
                target_model=TouristicEvent,
                target_pk=near_touristicevent,
            )

        near_touristiccontent = request.GET.get("near_touristiccontent")
        if near_touristiccontent:
            qs = _filter_near(
                base_model=qs.model,
                queryset=qs,
                target_model=TouristicContent,
                target_pk=near_touristiccontent,
            )

        near_trek = request.GET.get("near_trek")
        if near_trek:
            qs = _filter_near(
                base_model=qs.model, queryset=qs, target_model=Trek, target_pk=near_trek
            )

        if "geotrek.outdoor" in settings.INSTALLED_APPS:
            near_outdoorsite = request.GET.get("near_outdoorsite")
            if near_outdoorsite:
                qs = _filter_near(
                    base_model=qs.model,
                    queryset=qs,
                    target_model=Site,
                    target_pk=near_outdoorsite,
                )

            near_outdoorcourse = request.GET.get("near_outdoorcourse")
            if near_outdoorcourse:
                qs = _filter_near(
                    base_model=qs.model,
                    queryset=qs,
                    target_model=Course,
                    target_pk=near_outdoorcourse,
                )
        return qs

    def get_schema_operation_parameters(self, view):
        parameters = [
            {
                "name": "near_trek",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by a trek id. It will only show the contents related to this trek."
                ),
                "schema": {"type": "integer"},
            },
            {
                "name": "near_touristiccontent",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by a touristic content id. It will only show the contents related to this touristic content."
                ),
                "schema": {"type": "integer"},
            },
            {
                "name": "near_touristicevent",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by a touristic event id. It will only show the contents related to this touristic event."
                ),
                "schema": {"type": "integer"},
            },
        ]
        if "geotrek.outdoor" in settings.INSTALLED_APPS:
            parameters += [
                {
                    "name": "near_outdoorsite",
                    "required": False,
                    "in": "query",
                    "description": _(
                        "Filter by an outdoor site id. It will only show the contents related to this outdoor site."
                    ),
                    "schema": {"type": "integer"},
                },
                {
                    "name": "near_outdoorcourse",
                    "required": False,
                    "in": "query",
                    "description": _(
                        "Filter by an outdoor course id. It will only show the contents related to this outdoor course."
                    ),
                    "schema": {"type": "integer"},
                },
            ]
        return parameters


class GeotrekZoningAndThemeFilter(BaseFilterBackend):
    def _filter_queryset(self, request, queryset, view):
        qs = queryset
        cities = request.GET.get("cities")
        if cities:
            qs = qs.filter(
                Exists(
                    City.objects.filter(
                        pk__in=cities.split(","), geom__intersects=OuterRef("geom")
                    )
                )
            )
        districts = request.GET.get("districts")
        if districts:
            qs = qs.filter(
                Exists(
                    District.objects.filter(
                        pk__in=districts.split(","), geom__intersects=OuterRef("geom")
                    )
                )
            )
        structures = request.GET.get("structures")
        if structures:
            qs = qs.filter(structure__in=structures.split(","))
        themes = request.GET.get("themes")
        portals = request.GET.get("portals")
        q = request.GET.get("q")
        if queryset.model.__name__ == "Course":
            if themes:
                qs = qs.filter(parent_sites__themes__in=themes.split(","))
            if portals:
                qs = qs.filter(parent_sites__portal__in=portals.split(","))
            if q:
                qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        else:
            if themes:
                qs = qs.filter(themes__in=themes.split(","))
            if portals:
                qs = qs.filter(portal__in=portals.split(","))
            if q:
                qs = qs.filter(
                    Q(name__icontains=q)
                    | Q(description__icontains=q)
                    | Q(description_teaser__icontains=q)
                )
        return qs

    def _get_schema_operation_parameters(self, view):
        return [
            {
                "name": "cities",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more city id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "districts",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more district id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "structures",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or more structure id, comma-separated."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "themes",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more themes id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "portals",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more portal id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "q",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by some case-insensitive text contained in name, description teaser or description."
                ),
                "schema": {"type": "string"},
            },
        ]


class GeotrekInformationDeskFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        qs = queryset
        types = request.GET.get("types")
        if types:
            qs = qs.filter(type__in=types.split(","))
        trek = request.GET.get("trek", None)
        if trek is not None:
            qs = qs.filter(treks__id=trek)
        labels_accessibility = request.GET.get("labels_accessibility")
        if labels_accessibility:
            qs = qs.filter(label_accessibility__in=labels_accessibility.split(","))
        return qs

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "types",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or more types id, comma-separated. Logical OR for types in the same list, AND for types in different lists."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "labels_accessibility",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or more labels accessibility id, comma-separated."
                ),
                "schema": {"type": "string"},
            },
        ]


class GeotrekTouristicContentFilter(GeotrekZoningAndThemeFilter):
    def filter_queryset(self, request, queryset, view):
        qs = queryset
        categories = request.GET.get("categories")
        if categories:
            qs = qs.filter(category__in=categories.split(","))
        types = request.GET.get("types")
        if types:
            types_id = types.split(",")
            if TouristicContentType.objects.filter(id__in=types_id, in_list=1).exists():
                qs = qs.filter(Q(type1__in=types_id))
            if TouristicContentType.objects.filter(id__in=types_id, in_list=2).exists():
                qs = qs.filter(Q(type2__in=types_id))
        labels_accessibility = request.GET.get("labels_accessibility")
        if labels_accessibility:
            qs = qs.filter(label_accessibility__in=labels_accessibility.split(","))
        return self._filter_queryset(request, qs, view)

    def get_schema_operation_parameters(self, view):
        return self._get_schema_operation_parameters(view) + [
            {
                "name": "categories",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more category id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "types",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or more types id, comma-separated. Logical OR for types in the same list, AND for types in different lists."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "labels_accessibility",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or more labels accessibility id, comma-separated."
                ),
                "schema": {"type": "string"},
            },
        ]


class TouristicEventFilterSet(filters.FilterSet):
    place = ModelMultipleChoiceFilter(
        widget=CSVWidget(),
        queryset=TouristicEventPlace.objects.all(),
        help_text=_("Filter by one or more Place id, comma-separated."),
    )
    organizer = filters.ModelMultipleChoiceFilter(
        widget=CSVWidget(),
        queryset=TouristicEventOrganizer.objects.all(),
        help_text=_("Filter by one or more organizer, comma-separated."),
        field_name="organizers",
    )

    help_texts = {
        "bookable": _("Filter events on bookable boolean : true/false expected"),
        "cancelled": _("Filter events on cancelled boolean : true/false expected"),
    }

    @classmethod
    def filter_for_field(cls, f, name, lookup_expr):
        field_filter = super().filter_for_field(f, name, lookup_expr)
        field_filter.extra["help_text"] = cls.help_texts[name]
        return field_filter

    class Meta:
        model = TouristicEvent
        fields = ["cancelled", "bookable", "place", "organizer"]


class GeotrekTouristicEventFilter(GeotrekZoningAndThemeFilter):
    def filter_queryset(self, request, queryset, view):
        qs = queryset
        # Don't filter on detail view
        if "pk" not in view.kwargs:
            types = request.GET.get("types")
            if types:
                types_id = types.split(",")
                if TouristicEventType.objects.filter(id__in=types_id).exists():
                    qs = qs.filter(Q(type__in=types_id))
            dates_before = request.GET.get("dates_before")
            if dates_before:
                dates_before = datetime.strptime(dates_before, "%Y-%m-%d").date()
                qs = qs.filter(Q(begin_date__lte=dates_before))
            dates_after = request.GET.get("dates_after")
            if dates_after:
                dates_after = datetime.strptime(dates_after, "%Y-%m-%d").date()
                qs = qs.filter(
                    Q(end_date__gte=dates_after)
                    | Q(end_date__isnull=True) & Q(begin_date__gte=dates_after)
                )
            if not dates_after and not dates_before:
                # Filter out past events by default
                dates_after = date.today()
                qs = qs.filter(
                    Q(end_date__gte=dates_after)
                    | Q(end_date__isnull=True) & Q(begin_date__gte=dates_after)
                )
        return self._filter_queryset(request, qs, view)

    def get_schema_operation_parameters(self, view):
        return self._get_schema_operation_parameters(view) + [
            {
                "name": "types",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or more types id, comma-separated. Logical OR for types in the same list, AND for types in different lists."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "dates_before",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter events happening before or during date, format YYYY-MM-DD"
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "dates_after",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter events happening after or during date, format YYYY-MM-DD"
                ),
                "schema": {"type": "string"},
            },
        ]


class GeotrekServiceFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        qs = queryset
        types = request.GET.get("types")
        if types:
            types_id = types.split(",")
            if ServiceType.objects.filter(id__in=types_id).exists():
                qs = qs.filter(Q(type__in=types_id))
        qs = qs.filter(type__published=True)
        return qs

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "types",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or more types id, comma-separated. Logical OR for types in the same list, AND for types in different lists."
                ),
                "schema": {"type": "string"},
            },
        ]


class UpdateOrCreateDateFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        qs = queryset
        updated_before = request.GET.get("updated_before")
        if updated_before:
            qs = qs.filter(date_update__date__lte=updated_before)
        updated_after = request.GET.get("updated_after")
        if updated_after:
            qs = qs.filter(date_update__date__gte=updated_after)
        created_before = request.GET.get("created_before")
        if created_before:
            qs = qs.filter(date_insert__date__lte=created_before)
        created_after = request.GET.get("created_after")
        if created_after:
            qs = qs.filter(date_insert__date__gte=created_after)
        return qs

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "updated_after",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter objects updated after or during date, format YYYY-MM-DD"
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "updated_before",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter objects updated before or during date, format YYYY-MM-DD"
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "created_after",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter objects created after or during date, format YYYY-MM-DD"
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "created_before",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter objects created before or during date, format YYYY-MM-DD"
                ),
                "schema": {"type": "string"},
            },
        ]


class GeotrekTrekQueryParamsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        qs = queryset
        duration_min = request.GET.get("duration_min")
        if duration_min:
            qs = qs.filter(duration__gte=duration_min)
        duration_max = request.GET.get("duration_max")
        if duration_max:
            qs = qs.filter(duration__lte=duration_max)
        length_min = request.GET.get("length_min")
        if length_min:
            qs = qs.filter(length__gte=length_min)
        length_max = request.GET.get("length_max")
        if length_max:
            qs = qs.filter(length__lte=length_max)
        difficulty_min = request.GET.get("difficulty_min")
        if difficulty_min:
            qs = qs.filter(difficulty__id__gte=difficulty_min)
        difficulty_max = request.GET.get("difficulty_max")
        if difficulty_max:
            qs = qs.filter(difficulty__id__lte=difficulty_max)
        ascent_min = request.GET.get("ascent_min")
        if ascent_min:
            qs = qs.filter(ascent__gte=ascent_min)
        ascent_max = request.GET.get("ascent_max")
        if ascent_max:
            qs = qs.filter(ascent__lte=ascent_max)
        cities = request.GET.get("cities")
        if cities:
            qs = qs.filter(
                Exists(
                    City.objects.filter(
                        pk__in=cities.split(","), geom__intersects=OuterRef("geom")
                    )
                )
            )
        districts = request.GET.get("districts")
        if districts:
            qs = qs.filter(
                Exists(
                    District.objects.filter(
                        pk__in=districts.split(","), geom__intersects=OuterRef("geom")
                    )
                )
            )
        structures = request.GET.get("structures")
        if structures:
            qs = qs.filter(structure__in=structures.split(","))
        accessibilities = request.GET.get("accessibilities")
        if accessibilities:
            qs = qs.filter(accessibilities__in=accessibilities.split(","))
        accessibility_level = request.GET.get("accessibility_level")
        if accessibility_level:
            qs = qs.filter(accessibility_level__in=accessibility_level.split(","))
        themes = request.GET.get("themes")
        if themes:
            qs = qs.filter(themes__in=themes.split(","))
        portals = request.GET.get("portals")
        if portals:
            qs = qs.filter(portal__in=portals.split(","))
        route = request.GET.get("routes")
        if route:
            qs = qs.filter(route__in=route.split(","))
        labels = request.GET.get("labels")
        if labels:
            qs = qs.filter(labels__in=labels.split(","))
        labels_exclude = request.GET.get("labels_exclude")
        if labels_exclude:
            qs = qs.exclude(labels__in=labels_exclude.split(","))
        practices = request.GET.get("practices")
        if practices:
            qs = qs.filter(practice__in=practices.split(","))
        q = request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(description_teaser__icontains=q)
                | Q(ambiance__icontains=q)
            )
        return qs.distinct()

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "duration_min",
                "required": False,
                "in": "query",
                "description": _("Filter by minimum duration (hours)."),
                "schema": {"type": "number"},
            },
            {
                "name": "duration_max",
                "required": False,
                "in": "query",
                "description": _("Filter by maximum duration (hours)."),
                "schema": {"type": "number"},
            },
            {
                "name": "length_min",
                "required": False,
                "in": "query",
                "description": _("Filter by minimum length (meters)."),
                "schema": {"type": "integer"},
            },
            {
                "name": "length_max",
                "required": False,
                "in": "query",
                "description": _("Filter by maximum length (meters)."),
                "schema": {"type": "integer"},
            },
            {
                "name": "difficulty_min",
                "required": False,
                "in": "query",
                "description": _("Filter by minimum difficulty level (id)."),
                "schema": {"type": "integer"},
            },
            {
                "name": "difficulty_max",
                "required": False,
                "in": "query",
                "description": _("Filter by maximum difficulty level (id)."),
                "schema": {"type": "integer"},
            },
            {
                "name": "ascent_min",
                "required": False,
                "in": "query",
                "description": _("Filter by minimum ascent (meters)."),
                "schema": {"type": "integer"},
            },
            {
                "name": "ascent_max",
                "required": False,
                "in": "query",
                "description": _("Filter by maximum ascent (meters)."),
                "schema": {"type": "integer"},
            },
            {
                "name": "cities",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more city id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "districts",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more district id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "structures",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or more structure id, comma-separated."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "accessibilities",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or more type of accessibility id, comma-separated."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "accessibility_level",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or more accessibility level id, comma-separated."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "themes",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more theme id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "portals",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more portal id, comma-separateds."),
                "schema": {"type": "string"},
            },
            {
                "name": "routes",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more route id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "labels",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more label id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "labels_exclude",
                "required": False,
                "in": "query",
                "description": _("Exclude one or more label id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "practices",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more practice id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "q",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by some case-insensitive text contained in name, description, description teaser or ambiance."
                ),
                "schema": {"type": "string"},
            },
        ]


class GeotrekRatingsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        ratings = request.GET.get("ratings")
        if ratings:
            queryset = queryset.filter(ratings__in=ratings.split(","))
        return queryset

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "ratings",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more ratings id, comma-separated."),
                "schema": {"type": "string"},
            },
        ]


class GeotrekNetworksFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        networks = request.GET.get("networks")
        if networks:
            queryset = queryset.filter(networks__in=networks.split(","))
        return queryset

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "networks",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more networks id, comma-separated."),
                "schema": {"type": "string"},
            },
        ]


class GeotrekSiteFilter(GeotrekZoningAndThemeFilter):
    def filter_queryset(self, request, queryset, view):
        root_sites_only = request.GET.get("root_sites_only")
        if root_sites_only:
            # Being a root node <=> having no parent
            queryset = queryset.filter(parent=None)
        practices_in_hierarchy = request.GET.get("practices_in_hierarchy")
        # TODO Optimize this filter by finding an alternative to queryset iterating
        if practices_in_hierarchy:
            wanted_practices = set(map(int, practices_in_hierarchy.split(",")))
            for site in queryset:
                # Exclude if practices in hierarchy don't match any wanted practices
                found_practices = site.super_practices_id
                if found_practices.isdisjoint(wanted_practices):
                    queryset = queryset.exclude(id=site.pk)
        # TODO Optimize this filter by finding an alternative to queryset iterating
        ratings_in_hierarchy = request.GET.get("ratings_in_hierarchy")
        if ratings_in_hierarchy:
            wanted_ratings = set(map(int, ratings_in_hierarchy.split(",")))
            for site in queryset:
                # Exclude if ratings in hierarchy don't match any wanted ratings
                found_ratings = site.super_ratings_id
                if found_ratings.isdisjoint(wanted_ratings):
                    queryset = queryset.exclude(id=site.pk)
        types = request.GET.get("types")
        if types:
            queryset = queryset.filter(type__in=types.split(","))
        labels = request.GET.get("labels")
        if labels:
            queryset = queryset.filter(labels__in=labels.split(","))
        labels_exclude = request.GET.get("labels_exclude")
        if labels_exclude:
            queryset = queryset.exclude(labels__in=labels_exclude.split(","))
        return self._filter_queryset(request, queryset, view)

    def get_schema_operation_parameters(self, view):
        return self._get_schema_operation_parameters(view) + [
            {
                "name": "root_sites_only",
                "required": False,
                "in": "query",
                "description": _(
                    "Only return sites that are at the top of the hierarchy and have no parent. Use any string to activate."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "practices_in_hierarchy",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or more practices id, comma-separated. Return sites that have theses practices OR have at least one child site that does."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "types",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or more site type id, comma-separated."
                ),
                "schema": {"type": "string"},
            },
            {
                "name": "labels",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more label id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "labels_exclude",
                "required": False,
                "in": "query",
                "description": _("Exclude one or more label id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "ratings_in_hierarchy",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or more ratings id, comma-separated. Return sites that have theses ratings OR have at least one child site that does."
                ),
                "schema": {"type": "string"},
            },
        ]


class GeotrekCourseFilter(GeotrekZoningAndThemeFilter):
    def filter_queryset(self, request, queryset, view):
        practices = request.GET.get("practices")
        if practices:
            queryset = queryset.filter(parent_sites__isnull=False).distinct()
            queryset = queryset.filter(parent_sites__practice__isnull=False).distinct()
            queryset = queryset.filter(
                parent_sites__practice__in=practices.split(",")
            ).distinct()
        types = request.GET.get("types")
        if types:
            queryset = queryset.filter(type__in=types.split(","))
        return self._filter_queryset(request, queryset, view)

    def get_schema_operation_parameters(self, view):
        return self._get_schema_operation_parameters(view) + [
            {
                "name": "practices",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more practice id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "types",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by one or more course type id, comma-separated."
                ),
                "schema": {"type": "string"},
            },
        ]


class RelatedObjectsPublishedNotDeletedFilter(BaseFilterBackend):
    def filter_queryset_related_objects_published_not_deleted(
        self, qs, request, related_name, optional_query=Q()
    ):
        qs = qs.exclude(**{f"{related_name}": None})
        # Ensure no deleted content is taken in consideration in the filter
        related_field_name = f"{related_name}__deleted"
        optional_query &= Q(**{related_field_name: False})
        return self.filter_queryset_related_objects_published(
            qs, request, related_name, optional_query
        )

    def filter_queryset_related_objects_published(
        self, queryset, request, related_name, optional_query=Q()
    ):
        """
        TODO : this method is not optimal. the API should have a route /object returning all objects and /object/used returning only used objects.
        Return a queryset filtered by publication status or related objects.
        For example for a queryset of DifficultyLevels it will check the publication status of related treks and return the queryset of difficulties that are used by published treks.
        :param queryset: the queryset to filter
        :param request: the request object to get to the potential language to filter by
        :param related_name: the related_name used to fetch the related object in the filter method
        :param optional_query: optional query Q to add to the filter method (used by portal filter)
        """
        qs = queryset
        q = Q()
        # check if the model of the queryset published field is translated
        related_object = qs.model._meta.get_field(related_name).remote_field
        fields_on_related_object = related_object.model._meta.get_fields()
        associated_published_fields = [
            f.name for f in fields_on_related_object if f.name.startswith("published")
        ]
        if associated_published_fields:
            language = request.GET.get("language")
            if language:
                # one language is specified
                related_field_name = "{}__{}".format(
                    related_name, build_localized_fieldname("published", language)
                )
                q &= Q(**{related_field_name: True})
            else:
                # no language specified. Check for all.
                for lang in settings.MODELTRANSLATION_LANGUAGES:
                    related_field_name = "{}__{}".format(
                        related_name, build_localized_fieldname("published", lang)
                    )
                    q |= Q(**{related_field_name: True})
        q &= optional_query
        qs = qs.filter(q)
        return qs.distinct().order_by("pk")


class RelatedObjectsPublishedNotDeletedByPortalFilter(
    RelatedObjectsPublishedNotDeletedFilter
):
    def filter_queryset_related_objects_by_portal(self, request, related_name):
        portals = request.GET.get("portals")
        query = Q()
        if portals:
            related_portal_in = f"{related_name}__portal__in"
            query = Q(**{related_portal_in: portals.split(",")})
        return query

    def filter_queryset_related_objects_published_not_deleted_by_portal(
        self, qs, request, related_name
    ):
        # Exclude if no related objects exist
        qs = qs.exclude(**{f"{related_name}": None})
        portal_query = self.filter_queryset_related_objects_by_portal(
            request, related_name
        )
        return self.filter_queryset_related_objects_published_not_deleted(
            qs, request, related_name, portal_query
        )

    def filter_queryset_related_objects_published_by_portal(
        self, qs, request, related_name
    ):
        # Exclude if no related objects exist
        qs = qs.exclude(**{f"{related_name}": None})
        portal_query = self.filter_queryset_related_objects_by_portal(
            request, related_name
        )
        return self.filter_queryset_related_objects_published(
            qs, request, related_name, portal_query
        )

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "portals",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more portal id, comma-separateds."),
                "schema": {"type": "string"},
            },
        ]


class TrekRelatedPortalFilter(RelatedObjectsPublishedNotDeletedByPortalFilter):
    def filter_queryset(self, request, qs, view):
        return self.filter_queryset_related_objects_published_not_deleted_by_portal(
            qs, request, "treks"
        )


class SignageRelatedPortalFilter(RelatedObjectsPublishedNotDeletedByPortalFilter):
    def filter_queryset(self, request, qs, view):
        return self.filter_queryset_related_objects_published_not_deleted_by_portal(
            qs, request, "signages"
        )


class InfrastructureRelatedPortalFilter(
    RelatedObjectsPublishedNotDeletedByPortalFilter
):
    def filter_queryset(self, request, qs, view):
        return self.filter_queryset_related_objects_published_not_deleted_by_portal(
            qs, request, "infrastructures"
        )


class TouristicEventRelatedPortalFilter(
    RelatedObjectsPublishedNotDeletedByPortalFilter
):
    def filter_queryset(self, request, qs, view):
        return self.filter_queryset_related_objects_published_not_deleted_by_portal(
            qs, request, "touristicevent"
        )


class TouristicEventsRelatedPortalFilter(
    RelatedObjectsPublishedNotDeletedByPortalFilter
):
    def filter_queryset(self, request, qs, view):
        return self.filter_queryset_related_objects_published_not_deleted_by_portal(
            qs, request, "touristicevents"
        )


class SiteRelatedPortalFilter(RelatedObjectsPublishedNotDeletedByPortalFilter):
    def filter_queryset(self, request, qs, view):
        return self.filter_queryset_related_objects_published_by_portal(
            qs, request, "sites"
        )


class CourseRelatedFilter(RelatedObjectsPublishedNotDeletedFilter):
    def filter_queryset(self, request, qs, view):
        return self.filter_queryset_related_objects_published(qs, request, "courses")


class SitesRelatedPortalAndCourseRelatedFilter(
    RelatedObjectsPublishedNotDeletedByPortalFilter
):
    def filter_queryset(self, request, qs, view):
        set_1 = self.filter_queryset_related_objects_published(qs, request, "courses")
        set_2 = self.filter_queryset_related_objects_published_by_portal(
            qs, request, "sites"
        )
        return (set_1 | set_2).distinct()


class RelatedPortalStructureOrReservationSystemFilter(
    RelatedObjectsPublishedNotDeletedByPortalFilter
):
    def filter_queryset(self, request, qs, view):
        set_1 = self.filter_queryset_related_objects_published_not_deleted_by_portal(
            qs, request, "trek"
        )
        set_2 = self.filter_queryset_related_objects_published_not_deleted_by_portal(
            qs, request, "touristiccontent"
        )
        return (set_1 | set_2).distinct()


class TouristicContentRelatedPortalFilter(
    RelatedObjectsPublishedNotDeletedByPortalFilter
):
    def filter_queryset(self, request, qs, view):
        return self.filter_queryset_related_objects_published_not_deleted_by_portal(
            qs, request, "contents"
        )


class HDViewPointPublishedByPortalFilter(
    RelatedObjectsPublishedNotDeletedByPortalFilter
):
    def filter_queryset_related_objects_published_not_deleted_by_portal(
        self, qs, request, related_name
    ):
        # ####################################
        # Should be :
        #       qs = qs.exclude(**{'{}'.format(related_name): None})
        # But we need to bypass this bug : https://code.djangoproject.com/ticket/26261
        # TODO Revert when using Django > 4.2
        qs = qs.filter(**{f"{related_name}__isnull": False})
        # ####################################
        # Ensure no deleted content is taken in consideration in the filter
        portal_query = self.filter_queryset_related_objects_by_portal(
            request, related_name
        )
        related_field_name = f"{related_name}__deleted"
        portal_query &= Q(**{related_field_name: False})
        return self.filter_queryset_related_objects_published(
            qs, request, related_name, portal_query
        )

    def filter_queryset(self, request, qs, view):
        set_1 = self.filter_queryset_related_objects_published_not_deleted_by_portal(
            qs, request, "trek"
        )
        set_2 = self.filter_queryset_related_objects_published_not_deleted_by_portal(
            qs, request, "poi"
        )
        set_3 = qs.none()
        if "geotrek.outdoor" in settings.INSTALLED_APPS:
            related_name = "site"
            qs = qs.filter(**{f"{related_name}__isnull": False})
            portal_query = self.filter_queryset_related_objects_by_portal(
                request, related_name
            )
            set_3 = self.filter_queryset_related_objects_published(
                qs, request, related_name, portal_query
            )
        return (set_1 | set_2 | set_3).distinct()


class TreksAndSitesAndTourismRelatedPortalThemeFilter(
    RelatedObjectsPublishedNotDeletedByPortalFilter
):
    def filter_queryset(self, request, qs, view):
        set_1 = self.filter_queryset_related_objects_published_not_deleted_by_portal(
            qs, request, "treks"
        )
        set_2 = self.filter_queryset_related_objects_published_not_deleted_by_portal(
            qs, request, "touristiccontents"
        )
        set_3 = self.filter_queryset_related_objects_published_not_deleted_by_portal(
            qs, request, "touristic_events"
        )
        set_4 = qs.none()
        if "geotrek.outdoor" in settings.INSTALLED_APPS:
            set_4 = self.filter_queryset_related_objects_published_by_portal(
                qs, request, "sites"
            )
        return (set_1 | set_2 | set_3 | set_4).distinct()


class TreksAndSitesAndTourismAndFlatpagesRelatedPortalThemeFilter(
    RelatedObjectsPublishedNotDeletedByPortalFilter
):
    def filter_queryset(self, request, qs, view):
        # Prepare language query
        lang_query = Q()
        language = request.GET.get("language")
        if language:
            # one language is specified
            lang_query = Q(**{build_localized_fieldname("published", language): True})
        else:
            # no language specified. Check for all.
            for lang in settings.MODELTRANSLATION_LANGUAGES:
                lang_query |= Q(**{build_localized_fieldname("published", lang): True})

        # Prepare portal queries
        portals = request.GET.get("portals")
        if portals:
            portals_query = Q(**{"portals__in": portals.split(",")})
            portal_query = Q(**{"portal__in": portals.split(",")})
        else:
            portal_query = Q()
            portals_query = Q()

        # Extract distinct sources
        flatpages_sources = list(
            FlatPage.objects.filter(lang_query, portals_query)
            .prefetch_related("portals, source")
            .values_list("source__pk", flat=True)
        )
        treks_sources = list(
            Trek.objects.filter(lang_query, portal_query, deleted=False)
            .prefetch_related("portal, source")
            .values_list("source__pk", flat=True)
        )
        touristiccontent_sources = list(
            TouristicContent.objects.filter(lang_query, portal_query, deleted=False)
            .prefetch_related("portal, source")
            .values_list("source__pk", flat=True)
        )
        touristicevent_sources = list(
            TouristicEvent.objects.filter(lang_query, portal_query, deleted=False)
            .prefetch_related("portal, source")
            .values_list("source__pk", flat=True)
        )
        all_sources_pks = (
            flatpages_sources
            + treks_sources
            + touristiccontent_sources
            + touristicevent_sources
        )
        if "geotrek.outdoor" in settings.INSTALLED_APPS:
            sites_sources = list(
                Site.objects.filter(lang_query, portal_query)
                .prefetch_related("portal, source")
                .values_list("source__pk", flat=True)
            )
            all_sources_pks += sites_sources

        # Return distinct sources
        return qs.filter(pk__in=set(all_sources_pks))


class TreksAndSitesRelatedPortalFilter(RelatedObjectsPublishedNotDeletedByPortalFilter):
    def filter_queryset(self, request, qs, view):
        set_1 = self.filter_queryset_related_objects_published_not_deleted_by_portal(
            qs, request, "treks"
        )
        set_2 = qs.none()
        if "geotrek.outdoor" in settings.INSTALLED_APPS:
            set_2 = self.filter_queryset_related_objects_published_by_portal(
                qs, request, "sites"
            )
        return (set_1 | set_2).distinct()


class GeotrekRatingScaleFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        practices = request.GET.get("practices")
        if practices:
            queryset = queryset.filter(practice__in=practices.split(","))
        q = request.GET.get("q")
        if q:
            queryset = queryset.filter(name__icontains=q)
        return queryset

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "practices",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more practice id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "q",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by some case-insensitive text contained in name."
                ),
                "schema": {"type": "string"},
            },
        ]


class GeotrekLabelFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        queryset = queryset.filter(published=True)
        filter_label = request.GET.get("only_filters")
        if filter_label:
            try:
                # Allow to filter with many values for exemple for True : yes, true, t, True ...
                queryset = queryset.filter(filter=bool(strtobool(filter_label)))
            except ValueError:
                return queryset.none()
        return queryset

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "only_filters",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by the fact that this label can be used as filter. "
                    "'y', 'yes', 't', 'true', 'on', '1' are possible values"
                ),
                "schema": {"type": "boolean"},
            },
        ]


class GeotrekRatingFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        scale = request.GET.get("scale")
        if scale:
            queryset = queryset.filter(scale__pk=scale)
        q = request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(scale__name__icontains=q)
            )
        return queryset

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "scale",
                "required": False,
                "in": "query",
                "description": _("Filter by a rating scale id."),
                "schema": {"type": "integer"},
            },
            {
                "name": "q",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by some case-insensitive text contained in name, scale name or description."
                ),
                "schema": {"type": "string"},
            },
        ]


class MenuItemFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        portals = request.GET.get("portals")
        if portals:
            queryset = queryset.filter(portals__in=portals.split(","))
        return queryset

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "portals",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more portal id, comma-separated."),
                "schema": {"type": "string"},
            },
        ]


class FlatPageFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        parent_id = request.GET.get("parent")
        if parent_id:
            try:
                parent_page = FlatPage.objects.get(pk=parent_id)
            except FlatPage.DoesNotExist:
                return queryset.none()
            queryset = parent_page.get_children()
        sources = request.GET.get("sources")
        if sources:
            queryset = queryset.filter(source__in=sources.split(","))
        portals = request.GET.get("portals")
        if portals:
            language = request.GET.get("language", "all")
            published_menu_items = (
                MenuItem.objects.filter(
                    get_published_filter_expression(MenuItem, language)
                )
                .filter(portals__in=portals.split(","))
                .values_list("id", flat=True)
            )
            # Filter on Flat Pages associated to one of the portals
            # OR targeted by a published Menu Item associated to one of the portals.
            queryset = queryset.filter(
                Q(portals__in=portals.split(","))
                | Q(menu_items__id__in=published_menu_items)
            ).distinct()
        q = request.GET.get("q")
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(content__icontains=q))
        return queryset

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "parent",
                "required": False,
                "in": "query",
                "description": _("Filter by the parent page ID"),
                "schema": {"type": "integer"},
            },
            {
                "name": "sources",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more source id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "portals",
                "required": False,
                "in": "query",
                "description": _("Filter by one or more portal id, comma-separated."),
                "schema": {"type": "string"},
            },
            {
                "name": "q",
                "required": False,
                "in": "query",
                "description": _(
                    "Filter by some case-insensitive text contained in name or content."
                ),
                "schema": {"type": "string"},
            },
        ]
