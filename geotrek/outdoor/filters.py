from django.db.models import Q
from django.utils.translation import gettext as _
from django_filters.filters import MultipleChoiceFilter, ModelMultipleChoiceFilter
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.common.models import Organism
from geotrek.outdoor.models import Site, Practice, Sector, Course
from geotrek.zoning.filters import ZoningFilterSet


class SiteFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    orientation = MultipleChoiceFilter(choices=Site.ORIENTATION_CHOICES, method='filter_orientation')
    wind = MultipleChoiceFilter(choices=Site.WIND_CHOICES, method='filter_orientation')
    practice = ModelMultipleChoiceFilter(queryset=Practice.objects.all(), method='filter_super')
    sector = ModelMultipleChoiceFilter(queryset=Sector.objects.all(), method='filter_sector', label=_("Sector"))
    managers = ModelMultipleChoiceFilter(queryset=Organism.objects.all(), method='filter_manager', label=_("Manager"))

    class Meta(StructureRelatedFilterSet.Meta):
        model = Site
        fields = StructureRelatedFilterSet.Meta.fields + [
            'sector', 'practice', 'labels', 'themes', 'portal', 'source', 'information_desks',
            'web_links', 'type', 'orientation', 'wind',
        ]

    def filter_orientation(self, qs, name, values):
        q = Q()
        for value in values:
            q |= Q(**{'{}__contains'.format(name): value})
        return qs.filter(q).get_ancestors(include_self=True)

    def filter_super(self, qs, name, values):
        if not values:
            return qs
        return qs.filter(**{'{}__in'.format(name): values}).get_ancestors(include_self=True)

    def filter_sector(self, qs, name, values):
        if not values:
            return qs
        return qs.filter(practice__sector__in=values).get_ancestors(include_self=True)

    def filter_manager(self, qs, name, values):
        if not values:
            return qs
        return qs.filter(managers__in=values).get_ancestors(include_self=True)


class CourseFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    orientation = MultipleChoiceFilter(choices=Site.ORIENTATION_CHOICES, method='filter_orientation',
                                       label=_("Orientation"))
    wind = MultipleChoiceFilter(choices=Site.WIND_CHOICES, method='filter_orientation',
                                label=_("Wind"))

    class Meta(StructureRelatedFilterSet.Meta):
        model = Course
        fields = StructureRelatedFilterSet.Meta.fields + [
            'site', 'site__practice__sector', 'site__practice', 'site__labels', 'site__themes',
            'site__portal', 'site__source', 'site__type', 'orientation', 'wind',
            'height',
        ]

    def filter_orientation(self, qs, name, values):
        q = Q()
        for value in values:
            q |= Q(**{'site__{}__contains'.format(name): value})
        return qs.filter(q)
