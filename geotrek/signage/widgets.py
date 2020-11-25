from django.utils.translation import gettext_lazy as _

from geotrek.common.widgets import YearSelect
from geotrek.maintenance.filters import InterventionYearSelect
from geotrek.signage.models import Signage


class SignageYearSelect(InterventionYearSelect):
    label = _("Intervention year")


class SignageImplantationYearSelect(YearSelect):
    label = _("Implantation year")

    def get_years(self):
        return Signage.objects.all_implantation_years()
