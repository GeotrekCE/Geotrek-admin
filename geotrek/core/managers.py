from django.contrib.gis.db import models

from geotrek.common.functions import Length
from geotrek.common.mixins.managers import NoDeleteManager


class PathManager(models.Manager):
    # Use this manager when walking through FK/M2M relationships
    use_for_related_fields = True

    def get_queryset(self):
        """Hide all ``Path`` records that are not marked as visible.
        """
        return super().get_queryset().filter(visible=True).annotate(length_2d=Length('geom'))

    def provider_choices(self):
        providers = self.get_queryset().exclude(provider__exact='') \
            .distinct('provider').values_list('provider', 'provider')
        return providers


class PathInvisibleManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset()


class TopologyManager(NoDeleteManager):
    # Use this manager when walking through FK/M2M relationships
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().annotate(length_2d=Length('geom'))


class PathAggregationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('order')


class TrailManager(TopologyManager):
    def provider_choices(self):
        providers = self.get_queryset().existing().exclude(provider__exact='').order_by('provider') \
            .distinct('provider').values_list('provider', 'provider')
        return providers
