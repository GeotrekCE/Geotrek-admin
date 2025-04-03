from django.db.models import Case, Func, IntegerField, Max, Min, When
from django.db.models.functions import Cast, ExtractYear

from geotrek.common.mixins.managers import NoDeleteManager


class InterventionManager(NoDeleteManager):
    def year_choices(self):
        """Get all range years between begin_date and end_date and concatenates distinct years"""
        qs = (
            self.existing()
            .all()
            .annotate(
                years=Func(
                    Cast(ExtractYear("begin_date"), output_field=IntegerField()),
                    Cast(
                        Case(
                            When(end_date__isnull=False, then=ExtractYear("end_date")),
                            default=ExtractYear("begin_date"),
                        ),
                        output_field=IntegerField(),
                    ),
                    function="generate_series",
                ),
            )
        )
        values = qs.distinct("years").order_by("-years").values_list("years", flat=True)
        return [(year, year) for year in values]


class ProjectManager(NoDeleteManager):
    def year_choices(self):
        bounds = self.existing().aggregate(min=Min("begin_year"), max=Max("end_year"))
        if not bounds["min"] or not bounds["max"]:
            return []
        return [(year, year) for year in range(bounds["min"], bounds["max"] + 1)]
