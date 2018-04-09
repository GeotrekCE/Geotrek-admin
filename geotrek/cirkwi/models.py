from django.db import models
from django.utils.translation import ugettext_lazy as _


class CirkwiTag(models.Model):
    eid = models.IntegerField(verbose_name=_("Cirkwi id"), unique=True)
    name = models.CharField(verbose_name=_("Cirkwi name"), max_length=128, db_column='nom')

    class Meta:
        db_table = 'o_b_cirkwi_tag'
        verbose_name = _("Cirkwi tag")
        verbose_name_plural = _("Cirkwi tags")
        ordering = ['name']

    def __str__(self):
        return self.name


class CirkwiLocomotion(models.Model):
    eid = models.IntegerField(verbose_name=_("Cirkwi id"), unique=True)
    name = models.CharField(verbose_name=_("Cirkwi name"), max_length=128, db_column='nom')

    class Meta:
        db_table = 'o_b_cirkwi_locomotion'
        verbose_name = _("Cirkwi locomotion")
        verbose_name_plural = _("Cirkwi locomotions")
        ordering = ['name']

    def __str__(self):
        return self.name


class CirkwiPOICategory(models.Model):
    eid = models.IntegerField(verbose_name=_("Cirkwi id"), unique=True)
    name = models.CharField(verbose_name=_("Cirkwi name"), max_length=128, db_column='nom')

    class Meta:
        db_table = 'o_b_cirkwi_poi_category'
        verbose_name = _("Cirkwi POI category")
        verbose_name_plural = _("Cirkwi POI categories")
        ordering = ['name']

    def __str__(self):
        return self.name
