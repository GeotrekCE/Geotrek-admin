from django.utils.translation import pgettext_lazy
from django_filters.filters import ModelMultipleChoiceFilter
from geotrek.authent.filters import StructureRelatedFilterSet
from .models import SensitiveArea, Species


class SensitiveAreaFilterSet(StructureRelatedFilterSet):
    species = ModelMultipleChoiceFilter(
        label=pgettext_lazy("Singular", "Species"),
        queryset=Species.objects.filter(category=Species.SPECIES)
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = SensitiveArea
        fields = StructureRelatedFilterSet.Meta.fields + [
            'species', 'species__category',
        ]
