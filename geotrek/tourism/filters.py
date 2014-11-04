from geotrek.common.filters import StructureRelatedFilterSet

from .models import TouristicContent, TouristicEvent


class TouristicContentFilterSet(StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = TouristicContent
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'category', 'themes', 'type1', 'type2']


class TouristicEventFilterSet(StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = TouristicEvent
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'usage', 'themes', 'public']
