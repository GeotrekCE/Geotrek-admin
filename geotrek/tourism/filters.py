import django_filters.rest_framework
from django import forms
from django.utils.translation import gettext_lazy as _
from django.views.generic.dates import timezone_today
from django_filters.filters import ModelMultipleChoiceFilter, ModelChoiceFilter

from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.zoning.filters import ZoningFilterSet

from .models import (
    TouristicContent,
    TouristicContentType1,
    TouristicContentType2,
    TouristicEvent,
)
from geotrek.common.models import Provider


class TypeField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj!s} ({obj.category!s})"


class TypeFilter(ModelMultipleChoiceFilter):
    field_class = TypeField


class TouristicContentFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    type1 = TypeFilter(
        queryset=TouristicContentType1.objects.select_related("category").all()
    )
    type2 = TypeFilter(
        queryset=TouristicContentType2.objects.select_related("category").all()
    )
    provider = ModelMultipleChoiceFilter(
        label=_("Provider"),
        queryset=Provider.objects.filter(touristiccontent__isnull=False).distinct(),
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = TouristicContent
        fields = [
            *StructureRelatedFilterSet.Meta.fields,
            "published",
            "category",
            "type1",
            "type2",
            "themes",
            "approved",
            "source",
            "portal",
            "reservation_system",
            "provider",
        ]


class CompletedFilter(django_filters.BooleanFilter):
    """
    Filter events with end_date in past (event completed)
    """

    @property
    def field(self):
        field = super().field
        field.initial = False
        return field

    def filter(self, qs, value):
        queryset = qs

        if value is True:
            queryset = queryset.filter(end_date__lt=timezone_today())

        elif value is False:
            queryset = queryset.exclude(end_date__lt=timezone_today())

        return queryset


class TouristicEventFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    after = django_filters.DateFilter(
        label=_("After"), lookup_expr="gte", field_name="end_date"
    )
    before = django_filters.DateFilter(
        label=_("Before"), lookup_expr="lte", field_name="begin_date"
    )
    completed = CompletedFilter(label=_("Completed"))
    provider = ModelMultipleChoiceFilter(
        label=_("Provider"),
        queryset=Provider.objects.filter(touristicevent__isnull=False).distinct(),
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = TouristicEvent
        fields = [
            *StructureRelatedFilterSet.Meta.fields,
            "published",
            "type",
            "themes",
            "after",
            "before",
            "approved",
            "source",
            "portal",
            "provider",
            "bookable",
            "cancelled",
            "place",
        ]
