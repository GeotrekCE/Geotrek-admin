from django.db import models
from django.db.models import Manager as DefaultManager


class NoDeleteQuerySet(models.QuerySet):
    def existing(self):
        return self.filter(deleted=False)


class NoDeleteManager(DefaultManager):
    # Use this manager when walking through FK/M2M relationships
    use_for_related_fields = True

    def get_queryset(self):
        return NoDeleteQuerySet(self.model, using=self._db)

    # Filter out deleted objects
    def existing(self):
        return self.get_queryset().filter(deleted=False)
