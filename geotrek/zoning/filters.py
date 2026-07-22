from dal import autocomplete
from django.db.models import Exists, OuterRef, Q
from django.utils.translation import gettext_lazy as _
from django_filters import FilterSet, ModelMultipleChoiceFilter, filters

from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.common.filters import RightFilter
from geotrek.common.models import Provider
from geotrek.zoning.models import (
    City,
    District,
    RestrictedArea,
    RestrictedAreaType,
    VigilanceArea,
)


class IntersectionFilter(RightFilter):
    """Inherit from ``RightFilter``, just to make sure the widgets
    will be initialized the same way.
    """

    def filter(self, qs, value):
        q = Q()
        for subvalue in value:
            q |= Q(geom__intersects=subvalue.geom)
        return qs.filter(q)


class IntersectionFilterCity(IntersectionFilter):
    model = City


class IntersectionFilterDistrict(IntersectionFilter):
    model = District


class IntersectionFilterRestrictedAreaType(RightFilter):
    model = RestrictedAreaType

    def filter(self, qs, value):
        if not value:
            return qs
        return qs.filter(
            Exists(
                RestrictedArea.objects.filter(
                    area_type__in=value, geom__intersects=OuterRef("geom")
                )
            )
        )

    def get_queryset(self, request=None):
        return super().get_queryset().order_by("name")


class IntersectionFilterRestrictedArea(IntersectionFilter):
    queryset = RestrictedArea.objects.all().select_related("area_type")


class ZoningFilterSet(FilterSet):
    city = IntersectionFilterCity(
        label=_("City"),
        required=False,
        widget=autocomplete.ModelSelect2Multiple(
            url="zoning:city-autocomplete",
            attrs={
                "data-placeholder": _("City"),
            },
        ),
    )
    district = IntersectionFilterDistrict(
        label=_("District"),
        required=False,
        widget=autocomplete.ModelSelect2Multiple(
            url="zoning:district-autocomplete",
            attrs={
                "data-placeholder": _("District"),
            },
        ),
    )
    area_type = IntersectionFilterRestrictedAreaType(
        label=_("Restricted area type"),
        required=False,
        widget=autocomplete.Select2Multiple(),
    )
    area = IntersectionFilterRestrictedArea(
        label=_("Restricted area"),
        required=False,
        widget=autocomplete.ModelSelect2Multiple(
            url="zoning:restrictedarea-autocomplete",
            forward=["area_type"],
            attrs={
                "data-placeholder": _("Restricted area"),
            },
        ),
    )


class VigilanceAreaFilterSet(
    ZoningFilterSet,
    StructureRelatedFilterSet,
):
    name = filters.CharFilter(label=_("Name"), lookup_expr="icontains")
    provider = ModelMultipleChoiceFilter(
        label=_("Provider"),
        queryset=Provider.objects.filter(trek__isnull=False).distinct(),
        widget=autocomplete.Select2Multiple(),
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = VigilanceArea
        fields = [
            *StructureRelatedFilterSet.Meta.fields,
            "name",
            "published",
            "practicability",
            "vigilance_area_type",
            "sources",
            "portals",
            "provider",
        ]
