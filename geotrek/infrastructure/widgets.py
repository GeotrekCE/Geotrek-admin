from django.utils.translation import gettext_lazy as _

from geotrek.common.widgets import YearSelect
from geotrek.infrastructure.models import Infrastructure
from geotrek.maintenance.filters import InterventionYearSelect


class InfrastructureYearSelect(InterventionYearSelect):
    label = _("Intervention year")


class InfrastructureImplantationYearSelect(YearSelect):
    label = _("Implantation year")

    def get_years(self):
        return Infrastructure.objects.all_implantation_years()
