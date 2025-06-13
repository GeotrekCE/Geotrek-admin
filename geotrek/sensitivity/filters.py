from django.utils.translation import gettext as _
from django.utils.translation import pgettext_lazy
from django_filters.filters import ModelChoiceFilter, ModelMultipleChoiceFilter

from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.common.models import Provider

from .models import SensitiveArea, Species


class SensitiveAreaFilterSet(StructureRelatedFilterSet):
    species = ModelMultipleChoiceFilter(
        label=pgettext_lazy("Singular", "Species"),
        queryset=Species.objects.filter(category=Species.SPECIES),
    )
    provider = ModelChoiceFilter(
        queryset=Provider.objects.filter(sensitivearea__isnull=False).distinct(),
        empty_label=_("Provider")
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = SensitiveArea
        fields = [
            *StructureRelatedFilterSet.Meta.fields,
            "species",
            "species__category",
            "provider",
        ]
