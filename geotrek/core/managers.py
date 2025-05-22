from django.contrib.gis.db import models

from geotrek.common.functions import Length
from geotrek.common.mixins.managers import NoDeleteManager, ProviderChoicesMixin


class PathManager(models.Manager, ProviderChoicesMixin):
    # Use this manager when walking through FK/M2M relationships
    use_for_related_fields = True

    def get_queryset(self):
        """Hide all ``Path`` records that are not marked as visible."""
        return (
            super()
            .get_queryset()
            .filter(visible=True)
            .annotate(length_2d=Length("geom"))
        )


class PathInvisibleManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset()


class TopologyManager(NoDeleteManager):
    # Use this manager when walking through FK/M2M relationships
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().annotate(length_2d=Length("geom"))


class PathAggregationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("order")


class TrailManager(TopologyManager, ProviderChoicesMixin):
    pass
