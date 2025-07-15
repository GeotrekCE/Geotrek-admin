from geotrek.common.mixins.managers import NoDeleteManager


class SignageGISManager(NoDeleteManager):
    """Override default typology mixin manager, and filter by type."""

    def implantation_year_choices(self):
        values = (
            self.get_queryset()
            .existing()
            .filter(implantation_year__isnull=False)
            .order_by("-implantation_year")
            .distinct("implantation_year")
            .values_list("implantation_year", flat=True)
        )
        return tuple((value, value) for value in values)
