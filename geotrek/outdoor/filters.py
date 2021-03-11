from django.utils.translation import gettext as _
from django_filters.filters import MultipleChoiceFilter, ModelMultipleChoiceFilter
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.outdoor.models import Site, Practice, Sector, Course
from geotrek.zoning.filters import ZoningFilterSet


class SiteFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    orientation = MultipleChoiceFilter(choices=Site.ORIENTATION_CHOICES, method='filter_super')
    wind = MultipleChoiceFilter(choices=Site.ORIENTATION_CHOICES, method='filter_super')
    practice = ModelMultipleChoiceFilter(queryset=Practice.objects.all(), method='filter_super')
    sector = ModelMultipleChoiceFilter(queryset=Sector.objects.all(), method='filter_sector', label=_("Sector"))

    class Meta(StructureRelatedFilterSet.Meta):
        model = Site
        fields = StructureRelatedFilterSet.Meta.fields + [
            'sector', 'practice', 'labels', 'themes', 'portal', 'source', 'information_desks',
            'web_links', 'type', 'orientation', 'wind',
        ]

    def filter_super(self, qs, name, values):
        if not values:
            return qs
        return qs.filter(**{'{}__in'.format(name): values}).get_ancestors(include_self=True)

    def filter_sector(self, qs, name, values):
        if not values:
            return qs
        return qs.filter(practice__sector__in=values).get_ancestors(include_self=True)


class CourseFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = Course
        fields = StructureRelatedFilterSet.Meta.fields + [
            'site', 'site__practice__sector', 'site__practice', 'site__labels', 'site__themes',
            'site__portal', 'site__source', 'site__type', 'site__orientation', 'site__wind',
            'height',
        ]
