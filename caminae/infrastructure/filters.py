from django.forms.widgets import Select
from django.utils.translation import ugettext_lazy as _

from caminae.common.filters import StructureRelatedFilterSet
from caminae.mapentity.filters import YearFilter

from .models import INFRASTRUCTURE_TYPES, Infrastructure, Signage


class InfrastructureFilter(StructureRelatedFilterSet):
    intervention_year = YearFilter(name='interventions__date', widget=Select, label=_(u"Intervention year"))

    def __init__(self, *args, **kwargs):
        super(InfrastructureFilter, self).__init__(*args,**kwargs)
        field = self.form.fields['type']
        field.queryset = field.queryset.exclude(type=INFRASTRUCTURE_TYPES.SIGNAGE)

    class Meta(StructureRelatedFilterSet.Meta):
        model = Infrastructure
        fields = StructureRelatedFilterSet.Meta.fields + ['type']


class SignageFilter(StructureRelatedFilterSet):
    intervention_year = YearFilter(name='interventions__date', widget=Select, label=_(u"Intervention year"))

    def __init__(self, *args, **kwargs):
        super(SignageFilter, self).__init__(*args,**kwargs)
        field = self.form.fields['type']
        field.queryset = field.queryset.filter(type=INFRASTRUCTURE_TYPES.SIGNAGE)

    class Meta(StructureRelatedFilterSet.Meta):
        model = Signage
        fields = StructureRelatedFilterSet.Meta.fields + ['type']
