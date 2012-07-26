# -*- coding: utf-8 -*-


from django.db import models
from django.utils.translation import ugettext_lazy as _


class Organism(models.Model):

    code = models.IntegerField(primary_key=True)
    organism = models.CharField(max_length=128, verbose_name=_(u"Organism"))

    class Meta:
        db_table = 'liste_de_tous_les_organismes'
        verbose_name = _(u"Organism")
        verbose_name_plural = _(u"Organisms")

    def __unicode__(self):
        return self.organism


