from django.contrib.gis.db import models


class SelectableUserManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(userprofile__isnull=False)
