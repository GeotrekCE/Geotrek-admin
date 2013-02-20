from django.forms.widgets import Select
from django.utils.translation import ugettext_lazy as _

from caminae.mapentity.filters import YearFilter
from caminae.land.filters import EdgeStructureRelatedFilterSet

from .models import INFRASTRUCTURE_TYPES, Infrastructure, Signage


class InfrastructureFilter(EdgeStructureRelatedFilterSet):
    intervention_year = YearFilter(name='interventions__date', widget=Select, label=_(u"Intervention year"))

    def __init__(self, *args, **kwargs):
        super(InfrastructureFilter, self).__init__(*args, **kwargs)
        field = self.form.fields['type']
        field.queryset = field.queryset.exclude(type=INFRASTRUCTURE_TYPES.SIGNAGE)

    class Meta(EdgeStructureRelatedFilterSet.Meta):
        model = Infrastructure
        fields = EdgeStructureRelatedFilterSet.Meta.fields + ['type']


class SignageFilter(EdgeStructureRelatedFilterSet):
    intervention_year = YearFilter(name='interventions__date', widget=Select, label=_(u"Intervention year"))

    def __init__(self, *args, **kwargs):
        super(SignageFilter, self).__init__(*args, **kwargs)
        field = self.form.fields['type']
        field.queryset = field.queryset.filter(type=INFRASTRUCTURE_TYPES.SIGNAGE)

    class Meta(EdgeStructureRelatedFilterSet.Meta):
        model = Signage
        fields = EdgeStructureRelatedFilterSet.Meta.fields + ['type']

