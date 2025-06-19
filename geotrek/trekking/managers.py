from django.contrib.gis.db import models

from geotrek.common.mixins.managers import NoDeleteManager
from geotrek.core.managers import TopologyManager


class TrekOrderedChildManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        # Select treks foreign keys by default
        qs = super().get_queryset().select_related("parent", "child")
        # Exclude deleted treks
        return qs.exclude(parent__deleted=True).exclude(child__deleted=True)


class TrekManager(TopologyManager):
    pass


class WebLinkManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("category")


class POIManager(NoDeleteManager):
    pass


class ServiceManager(NoDeleteManager):
    pass
