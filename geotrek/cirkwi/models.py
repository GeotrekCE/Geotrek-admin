from django.db import models
from django.utils.translation import ugettext_lazy as _


class CirkwiTag(models.Model):
    eid = models.IntegerField(verbose_name=_(u"Cirkwi id"), unique=True)
    name = models.CharField(verbose_name=_(u"Cirkwi name"), max_length=128, db_column='nom')

    class Meta:
        db_table = 'o_b_cirkwi_tag'
        verbose_name = _(u"Cirkwi tag")
        verbose_name_plural = _(u"Cirkwi tags")
        ordering = ['name']

    def __unicode__(self):
        return self.name


class CirkwiLocomotion(models.Model):
    eid = models.IntegerField(verbose_name=_(u"Cirkwi id"), unique=True)
    name = models.CharField(verbose_name=_(u"Cirkwi name"), max_length=128, db_column='nom')

    class Meta:
        db_table = 'o_b_cirkwi_locomotion'
        verbose_name = _(u"Cirkwi locomotion")
        verbose_name_plural = _(u"Cirkwi locomotions")
        ordering = ['name']

    def __unicode__(self):
        return self.name


class CirkwiPOICategory(models.Model):
    eid = models.IntegerField(verbose_name=_(u"Cirkwi id"), unique=True)
    name = models.CharField(verbose_name=_(u"Cirkwi name"), max_length=128, db_column='nom')

    class Meta:
        db_table = 'o_b_cirkwi_poi_category'
        verbose_name = _(u"Cirkwi POI category")
        verbose_name_plural = _(u"Cirkwi POI categories")
        ordering = ['name']

    def __unicode__(self):
        return self.name
