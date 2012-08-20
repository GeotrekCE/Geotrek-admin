from caminae.common.filters import StructureRelatedFilterSet

from .models import Infrastructure, Signage


class InfrastructureFilter(StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = Infrastructure
        fields = StructureRelatedFilterSet.Meta.fields + ['type']


class SignageFilter(StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = Signage
        fields = StructureRelatedFilterSet.Meta.fields + ['type']
