from caminae.mapentity.filters import MapEntityFilterSet

from .models import Infrastructure, Signage


class InfrastructureFilter(MapEntityFilterSet):
    class Meta(MapEntityFilterSet.Meta):
        model = Infrastructure
        fields = MapEntityFilterSet.Meta.fields + ['type']


class SignageFilter(MapEntityFilterSet):
    class Meta(MapEntityFilterSet.Meta):
        model = Signage
        fields = MapEntityFilterSet.Meta.fields + ['type']
