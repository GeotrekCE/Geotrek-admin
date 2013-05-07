from django.db import models
from django.utils.translation import ugettext_lazy as _


class Organism(models.Model):

    organism = models.CharField(max_length=128, verbose_name=_(u"Organism"), db_column='organisme')

    class Meta:
        db_table = 'm_b_organisme'
        verbose_name = _(u"Organism")
        verbose_name_plural = _(u"Organisms")
        ordering = ['organism']

    def __unicode__(self):
        return self.organism
