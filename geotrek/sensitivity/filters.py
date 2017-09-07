from geotrek.common.filters import StructureRelatedFilterSet
from .models import SensitiveArea


class SensitiveAreaFilterSet(StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = SensitiveArea
        fields = StructureRelatedFilterSet.Meta.fields + [
            'species', 'category',
        ]
