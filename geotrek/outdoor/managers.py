from django.contrib.gis.db import models
from django.db.models import Manager
from mptt.managers import TreeManager


class SiteManager(TreeManager):
    def provider_choices(self):
        providers = self.get_queryset().exclude(provider__exact='').order_by('provider') \
            .distinct('provider').values_list('provider', 'provider')
        return providers


class CourseOrderedChildManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        # Select treks foreign keys by default
        return super(CourseOrderedChildManager, self).get_queryset().select_related('parent', 'child')


class CourseManager(Manager):
    def provider_choices(self):
        providers = self.get_queryset().exclude(provider__exact='').order_by('provider') \
            .distinct('provider').values_list('provider', 'provider')
        return providers
