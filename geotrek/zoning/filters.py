from dal import autocomplete
from django import forms
from django.db.models import Exists, OuterRef, Q
from django.utils.translation import gettext_lazy as _
from django_filters import (
    FilterSet,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
    filters,
)

from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.common.filters import BaseRightFilter, RightFilter
from geotrek.common.models import Provider
from geotrek.zoning.choices import Practicability
from geotrek.zoning.models import (
    City,
    District,
    RestrictedArea,
    RestrictedAreaType,
    VigilanceArea,
    VigilanceAreaType,
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


class IntersectionFilterVigilanceAreaType(RightFilter):
    model = VigilanceAreaType

    def filter(self, qs, value):
        if not value:
            return qs

        return qs.filter(
            Exists(
                VigilanceArea.objects.filter(
                    vigilance_area_type__in=value, geom__intersects=OuterRef("geom")
                )
            )
        )


class IntersectionFilterVigilanceAreaPracticability(
    BaseRightFilter, MultipleChoiceFilter
):
    def filter(self, qs, value):
        if not value:
            return qs

        return qs.filter(
            Exists(
                VigilanceArea.objects.filter(
                    practicability__in=value, geom__intersects=OuterRef("geom")
                )
            )
        )


class IntersectionFilterVigilanceArea(RightFilter):
    model = VigilanceArea

    def filter(self, qs, value):
        if not value:
            return qs

        return qs.filter(
            Exists(VigilanceArea.objects.filter(geom__intersects=OuterRef("geom")))
        )


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
    vigilance_area_type = IntersectionFilterVigilanceAreaType(
        label=_("Vigilance area type"),
        required=False,
        widget=autocomplete.Select2Multiple(),
    )
    vigilance_area_practicability = IntersectionFilterVigilanceAreaPracticability(
        label=_("Vigilance area Practicability"),
        required=False,
        widget=autocomplete.Select2Multiple(),
        choices=Practicability.choices,
    )
    vigilance_area = IntersectionFilterVigilanceArea(
        label=_("Vigilance area"),
        required=False,
        widget=autocomplete.ModelSelect2Multiple(
            url="zoning:vigilancearea-drf-autocomplete",
            forward=["vigilance_area_type", "vigilance_area_practicability"],
            attrs={
                "data-placeholder": _("Vigilance area"),
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
    type = ModelMultipleChoiceFilter(
        label=_("Vigilance area type"),
        queryset=VigilanceAreaType.objects.all(),
        widget=autocomplete.Select2Multiple(),
    )
    after = filters.DateFilter(
        label=_("After"),
        lookup_expr="gte",
        field_name="end_date",
        widget=forms.TextInput(attrs={"class": "form-control form-control-sm"}),
    )
    before = filters.DateFilter(
        label=_("Before"),
        lookup_expr="lte",
        field_name="start_date",
        widget=forms.TextInput(attrs={"class": "form-control form-control-sm"}),
    )
    period_active = filters.BooleanFilter(label=_("Period active"))
    active_today = filters.BooleanFilter(label=_("Active today"))

    class Meta(StructureRelatedFilterSet.Meta):
        model = VigilanceArea
        fields = [
            *StructureRelatedFilterSet.Meta.fields,
            "name",
            "published",
            "practicability",
            "sources",
            "portals",
            "provider",
            "period_active",
            "active_today",
        ]

    def __init__(self, *args, **kwargs):
        # Remove vigilance area filters from ZoningFilterSet
        self.base_filters.pop("vigilance_area_type", None)
        self.base_filters.pop("vigilance_area_practicability", None)
        self.base_filters.pop("vigilance_area", None)
        super().__init__(*args, **kwargs)
