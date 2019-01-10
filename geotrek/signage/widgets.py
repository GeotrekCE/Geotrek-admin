from django.utils.translation import ugettext_lazy as _

from geotrek.common.widgets import YearSelect
from geotrek.signage.models import Signage
from geotrek.maintenance.filters import InterventionYearSelect


class SignageYearSelect(InterventionYearSelect):
    label = _(u"Intervention year")


class SignageImplantationYearSelect(YearSelect):
    label = _(u"Implantation year")

    def get_years(self):
        return Signage.objects.all_implantation_years()
