from django.contrib.gis.db import models
from django.utils.translation import gettext as _

from geotrek.common.mixins.managers import NoDeleteManager


class PathManager(models.Manager):
    # Use this manager when walking through FK/M2M relationships
    use_for_related_fields = True

    def get_queryset(self):
        """Hide all ``Path`` records that are not marked as visible."""
        qs = super().get_queryset().filter(visible=True)
        qs = qs.extra(
            select={
                "name": "CASE WHEN name IS NULL OR name = '' THEN CONCAT(%s || ' ' || id) ELSE name END"
            },
            select_params=(_("path"),),
        )
        return qs


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
