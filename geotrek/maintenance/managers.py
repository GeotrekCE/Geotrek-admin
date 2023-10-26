from django.db.models import Min, Max
from django.db.models.functions import ExtractYear

from geotrek.common.mixins.managers import NoDeleteManager


class InterventionManager(NoDeleteManager):
    def year_choices(self):
        values = self.existing().filter(date__isnull=False).annotate(year=ExtractYear('date')) \
            .order_by('-year').distinct().values_list('year', flat=True)
        return [(year, year) for year in values]


class ProjectManager(NoDeleteManager):
    def year_choices(self):
        bounds = self.existing().aggregate(min=Min('begin_year'), max=Max('end_year'))
        if not bounds['min'] or not bounds['max']:
            return []
        return [(year, year) for year in range(bounds['min'], bounds['max'] + 1)]
