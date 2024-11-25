from django.contrib.gis.db import models

from geotrek.common.mixins.managers import NoDeleteManager, ProviderChoicesMixin, TimestampedChoicesMixin


class SelectableUserManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(userprofile__isnull=False)


class ReportManager(NoDeleteManager, TimestampedChoicesMixin, ProviderChoicesMixin):
    pass
