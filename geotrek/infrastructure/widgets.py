from django.utils.translation import gettext_lazy as _

from geotrek.maintenance.filters import InterventionYearSelect


class InfrastructureYearSelect(InterventionYearSelect):
    label = _("Intervention year")
