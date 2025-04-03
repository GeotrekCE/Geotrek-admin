from django.utils.translation import gettext as _
from django.utils.translation import pgettext_lazy
from django_filters.filters import ChoiceFilter, ModelMultipleChoiceFilter

from geotrek.authent.filters import StructureRelatedFilterSet

from .models import SensitiveArea, Species


class SensitiveAreaFilterSet(StructureRelatedFilterSet):
    species = ModelMultipleChoiceFilter(
        label=pgettext_lazy("Singular", "Species"),
        queryset=Species.objects.filter(category=Species.SPECIES),
    )
    provider = ChoiceFilter(
        field_name="provider",
        empty_label=_("Provider"),
        label=_("Provider"),
        choices=lambda: SensitiveArea.objects.provider_choices(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields["provider"].choices = SensitiveArea.objects.provider_choices()

    class Meta(StructureRelatedFilterSet.Meta):
        model = SensitiveArea
        fields = StructureRelatedFilterSet.Meta.fields + [
            "species",
            "species__category",
            "provider",
        ]
