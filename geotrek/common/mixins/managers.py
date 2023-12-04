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


class ProviderChoicesMixin:
    def provider_choices(self):
        qs = self.get_queryset()
        if hasattr(qs, "existing"):
            qs = qs.existing()
        values = qs.exclude(provider__exact='') \
            .distinct('provider').order_by("provider").values_list('provider', flat=True)
        return tuple((value, value) for value in values)
