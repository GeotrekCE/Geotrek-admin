from django.contrib.gis.db import models
from django.db.models import Manager
from mptt.managers import TreeManager

from geotrek.common.mixins.managers import ProviderChoicesMixin


class SiteManager(TreeManager, ProviderChoicesMixin):
    pass


class CourseOrderedChildManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        # Select treks foreign keys by default
        return super(CourseOrderedChildManager, self).get_queryset().select_related('parent', 'child')


class CourseManager(Manager, ProviderChoicesMixin):
    pass
