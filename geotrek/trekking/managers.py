from django.contrib.gis.db import models

from geotrek.common.mixins.managers import NoDeleteManager
from geotrek.core.managers import TopologyManager


class TrekOrderedChildManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        # Select treks foreign keys by default
        qs = super().get_queryset().select_related('parent', 'child')
        # Exclude deleted treks
        return qs.exclude(parent__deleted=True).exclude(child__deleted=True)


class TrekManager(TopologyManager):
    def provider_choices(self):
        providers = self.get_queryset().existing().order_by('provider').distinct('provider') \
            .exclude(provider__exact='').values_list('provider', 'provider')
        return providers


class TrekRelationshipManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        # Select treks foreign keys by default
        qs = super().get_queryset().select_related('trek_a', 'trek_b')
        # Exclude deleted treks
        return qs.exclude(trek_a__deleted=True).exclude(trek_b__deleted=True)


class WebLinkManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('category')


class POIManager(NoDeleteManager):
    def provider_choices(self):
        providers = self.get_queryset().existing().exclude(provider__exact='') \
            .distinct('provider').values_list('provider', 'provider')
        return providers


class ServiceManager(NoDeleteManager):
    def provider_choices(self):
        providers = self.get_queryset().existing().exclude(provider__exact='') \
            .distinct('provider').values_list('provider', 'provider')
        return providers
