from django.db import models
from django.db.models import Manager as DefaultManager
from django.utils.translation import ugettext_lazy as _

from geotrek.authent.models import StructureRelated


class TimeStampedModel(models.Model):
    # Computed values (managed at DB-level with triggers)
    date_insert = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_(u"Insertion date"), db_column='date_insert')
    date_update = models.DateTimeField(auto_now=True, editable=False, verbose_name=_(u"Update date"), db_column='date_update')

    class Meta:
        abstract = True


class NoDeleteMixin(models.Model):
    deleted = models.BooleanField(editable=False, default=False, db_column='supprime', verbose_name=_(u"Deleted"))

    def delete(self, force=False, using=None, **kwargs):
        if force:
            super(NoDeleteMixin, self).delete(using, **kwargs)
        else:
            self.deleted = True
            self.save(using=using)

    class Meta:
        abstract = True

    @classmethod
    def get_manager_cls(cls, parent_mgr_cls=DefaultManager):

        class NoDeleteManager(parent_mgr_cls):
            # Use this manager when walking through FK/M2M relationships
            use_for_related_fields = True

            # Filter out deleted objects
            def existing(self):
                return self.get_query_set().filter(deleted=False)

        return NoDeleteManager


class Organism(StructureRelated):

    organism = models.CharField(max_length=128, verbose_name=_(u"Organism"), db_column='organisme')

    class Meta:
        db_table = 'm_b_organisme'
        verbose_name = _(u"Organism")
        verbose_name_plural = _(u"Organisms")
        ordering = ['organism']

    def __unicode__(self):
        return self.organism
