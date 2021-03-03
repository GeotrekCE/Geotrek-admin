from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.zoning.filters import ZoningFilterSet

from .models import Dive


class DiveFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = Dive
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'difficulty', 'levels', 'themes',
            'practice', 'source', 'portal'
        ]
