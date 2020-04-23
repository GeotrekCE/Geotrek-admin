from django.utils.translation import ugettext_lazy as _

from geotrek.authent.models import Structure
from geotrek.common.widgets import ValueSelect, YearSelect
from geotrek.maintenance.filters import InterventionYearSelect
from geotrek.signage.models import Signage


class SignageYearSelect(InterventionYearSelect):
    label = _("Intervention year")


class SignageImplantationYearSelect(YearSelect):
    label = _("Implantation year")

    def get_years(self):
        return Signage.objects.all_implantation_years()


class SignageStructureSelect(ValueSelect):
    label = _("Related structure")

    def get_values(self):
        return Structure.objects.all()
