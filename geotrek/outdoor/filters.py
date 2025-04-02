from django.db.models import Q
from django.utils.translation import gettext as _
from django_filters.filters import (
    ChoiceFilter,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
)

from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.common.models import Organism
from geotrek.outdoor.models import Course, Practice, Sector, Site
from geotrek.zoning.filters import ZoningFilterSet


class SiteFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    orientation = MultipleChoiceFilter(
        choices=Site.ORIENTATION_CHOICES, method="filter_orientation"
    )
    wind = MultipleChoiceFilter(choices=Site.WIND_CHOICES, method="filter_orientation")
    practice = ModelMultipleChoiceFilter(
        queryset=Practice.objects.all(), method="filter_super"
    )
    sector = ModelMultipleChoiceFilter(
        queryset=Sector.objects.all(), method="filter_sector", label=_("Sector")
    )
    managers = ModelMultipleChoiceFilter(
        queryset=Organism.objects.all(), method="filter_manager", label=_("Manager")
    )
    provider = ChoiceFilter(
        field_name="provider",
        empty_label=_("Provider"),
        label=_("Provider"),
        choices=lambda: Site.objects.provider_choices(),
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = Site
        fields = StructureRelatedFilterSet.Meta.fields + [
            "published",
            "sector",
            "practice",
            "labels",
            "themes",
            "portal",
            "source",
            "information_desks",
            "web_links",
            "type",
            "orientation",
            "wind",
            "provider",
        ]

    def filter_orientation(self, qs, name, values):
        q = Q()
        for value in values:
            q |= Q(**{"{}__contains".format(name): value})
        return qs.filter(q).get_ancestors(include_self=True)

    def filter_super(self, qs, name, values):
        if not values:
            return qs
        return qs.filter(**{"{}__in".format(name): values}).get_ancestors(
            include_self=True
        )

    def filter_sector(self, qs, name, values):
        if not values:
            return qs
        return qs.filter(practice__sector__in=values).get_ancestors(include_self=True)

    def filter_manager(self, qs, name, values):
        if not values:
            return qs
        return qs.filter(managers__in=values).get_ancestors(include_self=True)


class CourseFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    orientation = MultipleChoiceFilter(
        choices=Site.ORIENTATION_CHOICES,
        method="filter_orientation",
        label=_("Orientation"),
    )
    wind = MultipleChoiceFilter(
        choices=Site.WIND_CHOICES, method="filter_orientation", label=_("Wind")
    )
    provider = ChoiceFilter(
        field_name="provider",
        empty_label=_("Provider"),
        label=_("Provider"),
        choices=lambda: Course.objects.provider_choices(),
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = Course
        fields = StructureRelatedFilterSet.Meta.fields + [
            "published",
            "parent_sites",
            "parent_sites__practice__sector",
            "parent_sites__practice",
            "parent_sites__labels",
            "parent_sites__themes",
            "parent_sites__portal",
            "parent_sites__source",
            "parent_sites__type",
            "orientation",
            "wind",
            "height",
            "provider",
        ]

    def filter_orientation(self, qs, name, values):
        q = Q()
        for value in values:
            q |= Q(**{"parent_sites__{}__contains".format(name): value})
        return qs.filter(q)
