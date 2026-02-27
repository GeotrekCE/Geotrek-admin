from django.contrib.gis.db import models

from geotrek.common.mixins.managers import NoDeleteManager


class PathManager(models.Manager):
    # Use this manager when walking through FK/M2M relationships
    use_for_related_fields = True


class PathInvisibleManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset()


class TopologyManager(NoDeleteManager):
    # Use this manager when walking through FK/M2M relationships
    use_for_related_fields = True


class PathAggregationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("order")


class TrailManager(TopologyManager):
    pass
