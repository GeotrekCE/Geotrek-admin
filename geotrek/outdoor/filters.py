from geotrek.common.filters import StructureRelatedFilterSet
from geotrek.outdoor.models import Site


class SiteFilterSet(StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = Site
        fields = StructureRelatedFilterSet.Meta.fields + [
            'practice',
        ]
