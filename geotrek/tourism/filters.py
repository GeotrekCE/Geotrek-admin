import django_filters.rest_framework
from django import forms
from django.utils.datetime_safe import datetime
from django.utils.translation import gettext_lazy as _
from django_filters.filters import ChoiceFilter, ModelMultipleChoiceFilter

from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.zoning.filters import ZoningFilterSet

from .models import (
    TouristicContent,
    TouristicContentType1,
    TouristicContentType2,
    TouristicEvent,
)


class TypeField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "{} ({})".format(str(obj), str(obj.category))


class TypeFilter(ModelMultipleChoiceFilter):
    field_class = TypeField


class TouristicContentFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    type1 = TypeFilter(queryset=TouristicContentType1.objects.all())
    type2 = TypeFilter(queryset=TouristicContentType2.objects.all())
    provider = ChoiceFilter(
        field_name='provider',
        empty_label=_("Provider"),
        label=_("Provider"),
        choices=lambda: TouristicContent.objects.provider_choices()
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = TouristicContent
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'category', 'type1', 'type2', 'themes',
            'approved', 'source', 'portal', 'reservation_system',
            'provider'
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
            queryset = queryset.filter(end_date__lt=datetime.today())

        elif value is False:
            queryset = queryset.exclude(end_date__lt=datetime.today())

        return queryset


class TouristicEventFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    after = django_filters.DateFilter(label=_("After"), lookup_expr='gte', field_name='end_date')
    before = django_filters.DateFilter(label=_("Before"), lookup_expr='lte', field_name='begin_date')
    completed = CompletedFilter(label=_("Completed"))
    provider = ChoiceFilter(
        field_name='provider',
        empty_label=_("Provider"),
        label=_("Provider"),
        choices=lambda: TouristicEvent.objects.provider_choices()
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = TouristicEvent
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'type', 'themes', 'after',
            'before', 'approved', 'source', 'portal', 'provider',
            'bookable', 'cancelled', 'place'
        ]
