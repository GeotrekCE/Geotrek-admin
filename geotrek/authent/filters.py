from mapentity.filters import MapEntityFilterSet


class StructureRelatedFilterSet(MapEntityFilterSet):
    class Meta(MapEntityFilterSet.Meta):
        fields = [*MapEntityFilterSet.Meta.fields, "structure"]
