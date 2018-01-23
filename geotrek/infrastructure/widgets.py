from django.utils.translation import ugettext_lazy as _

from geotrek.common.widgets import YearSelect
from geotrek.infrastructure.models import Signage, Infrastructure
from geotrek.maintenance.filters import InterventionYearSelect


class InfrastructureYearSelect(InterventionYearSelect):
    label = _(u"Intervention year")


class SignageImplantationYearSelect(YearSelect):
    label = _(u"Implantation year")

    def get_years(self):
        return Signage.objects.all_implantation_years()


class InfrastructureImplantationYearSelect(YearSelect):
    label = _(u"Implantation year")

    def get_years(self):
        return Infrastructure.objects.all_implantation_years()