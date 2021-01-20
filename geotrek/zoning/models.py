"""

   Zoning models
   (not MapEntity : just layers, on which intersections with objects is done in triggers)

"""
from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class RestrictedAreaType(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Name"))

    class Meta:
        verbose_name = _("Restricted area type")

    def __str__(self):
        return self.name


class RestrictedAreaManager(models.Manager):
    def get_queryset(self):
        return super(RestrictedAreaManager, self).get_queryset().select_related('area_type')


class RestrictedArea(models.Model):
    name = models.CharField(max_length=250, verbose_name=_("Name"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)
    area_type = models.ForeignKey(RestrictedAreaType, verbose_name=_("Restricted area"), on_delete=models.CASCADE)
    published = models.BooleanField(verbose_name=_("Published"), default=True, help_text=_("Visible on Geotrek-rando"))

    # Override default manager
    objects = RestrictedAreaManager()

    class Meta:
        ordering = ['area_type', 'name']
        verbose_name = _("Restricted area")
        verbose_name_plural = _("Restricted areas")

    def __str__(self):
        return "{} - {}".format(self.area_type.name, self.name)


class City(models.Model):
    code = models.CharField(primary_key=True, max_length=6)
    name = models.CharField(max_length=128, verbose_name=_("Name"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)
    published = models.BooleanField(verbose_name=_("Published"), default=True, help_text=_("Visible on Geotrek-rando"))

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
        ordering = ['name']

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("Name"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)
    published = models.BooleanField(verbose_name=_("Published"), default=True, help_text=_("Visible on Geotrek-rando"))

    class Meta:
        verbose_name = _("District")
        verbose_name_plural = _("Districts")
        ordering = ['name']

    def __str__(self):
        return self.name
