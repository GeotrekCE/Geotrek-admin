from caminae.common.filters import StructureRelatedFilterSet

from .models import INFRASTRUCTURE_TYPES, Infrastructure, Signage


class InfrastructureFilter(StructureRelatedFilterSet):
    def __init__(self, *args, **kwargs):
        super(InfrastructureFilter, self).__init__(*args,**kwargs)
        field = self.form.fields['type']
        field.queryset = field.queryset.exclude(type=INFRASTRUCTURE_TYPES.SIGNAGE)

    class Meta(StructureRelatedFilterSet.Meta):
        model = Infrastructure
        fields = StructureRelatedFilterSet.Meta.fields + ['type']


class SignageFilter(StructureRelatedFilterSet):
    def __init__(self, *args, **kwargs):
        super(SignageFilter, self).__init__(*args,**kwargs)
        field = self.form.fields['type']
        field.queryset = field.queryset.filter(type=INFRASTRUCTURE_TYPES.SIGNAGE)

    class Meta(StructureRelatedFilterSet.Meta):
        model = Signage
        fields = StructureRelatedFilterSet.Meta.fields + ['type']
