"""
   Sensitivity models
"""

import datetime

from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import pgettext_lazy, ugettext_lazy as _
from mapentity.models import MapEntityMixin
from geotrek.authent.models import StructureRelated
from geotrek.common.mixins import (PictogramMixin, NoDeleteMixin, TimeStampedModelMixin, AddPropertyMixin)
from geotrek.common.utils import intersecting
from geotrek.core.models import Topology


class SportPractice(models.Model):
    name = models.CharField(max_length=250, db_column='nom', verbose_name=_(u"Name"))

    class Meta:
        ordering = ['name']
        db_table = 's_b_pratique_sportive'
        verbose_name = _(u"Sport practice")
        verbose_name_plural = _(u"Sport practices")

    def __unicode__(self):
        return self.name


class Species(PictogramMixin):
    name = models.CharField(max_length=250, db_column='nom', verbose_name=_(u"Name"))
    period01 = models.BooleanField(default=False, db_column='periode01', verbose_name=_(u"January"))
    period02 = models.BooleanField(default=False, db_column='periode02', verbose_name=_(u"February"))
    period03 = models.BooleanField(default=False, db_column='periode03', verbose_name=_(u"March"))
    period04 = models.BooleanField(default=False, db_column='periode04', verbose_name=_(u"April"))
    period05 = models.BooleanField(default=False, db_column='periode05', verbose_name=_(u"May"))
    period06 = models.BooleanField(default=False, db_column='periode06', verbose_name=_(u"June"))
    period07 = models.BooleanField(default=False, db_column='periode07', verbose_name=_(u"July"))
    period08 = models.BooleanField(default=False, db_column='periode08', verbose_name=_(u"August"))
    period09 = models.BooleanField(default=False, db_column='periode09', verbose_name=_(u"September"))
    period10 = models.BooleanField(default=False, db_column='periode10', verbose_name=_(u"October"))
    period11 = models.BooleanField(default=False, db_column='periode11', verbose_name=_(u"November"))
    period12 = models.BooleanField(default=False, db_column='periode12', verbose_name=_(u"Decembre"))
    practices = models.ManyToManyField(SportPractice, db_table='s_r_espece_pratique_sportive', verbose_name=_(u"Sport practices"))
    url = models.URLField(blank=True, verbose_name="URL")

    class Meta:
        ordering = ['name']
        db_table = 's_b_espece'
        verbose_name = pgettext_lazy(u"Singular", u"Species")
        verbose_name_plural = _(u"Species")

    def __unicode__(self):
        return self.name


class SensitiveArea(MapEntityMixin, StructureRelated, TimeStampedModelMixin, NoDeleteMixin,
                    AddPropertyMixin):
    SPECIES = 1
    REGULATORY = 2
    geom = models.PolygonField(srid=settings.SRID)
    species = models.ForeignKey(Species, verbose_name=pgettext_lazy(u"Singular", u"Species"), db_column='espece')
    published = models.BooleanField(verbose_name=_(u"Published"), default=False,
                                    help_text=_(u"Online"), db_column='public')
    publication_date = models.DateField(verbose_name=_(u"Publication date"),
                                        null=True, blank=True, editable=False,
                                        db_column='date_publication')
    category = models.IntegerField(verbose_name=_(u"Category"), db_column='categorie',
                                   choices=((SPECIES, _(u"Species")), (REGULATORY, _(u"Regulatory"))))

    objects = NoDeleteMixin.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 's_t_zone_sensible'
        verbose_name = _(u"Sensitive area")
        verbose_name_plural = _(u"Sensitive areas")

    def __unicode__(self):
        return self.species.name

    def save(self, *args, **kwargs):
        if self.publication_date is None and self.published:
            self.publication_date = datetime.date.today()
        if self.publication_date is not None and not self.published:
            self.publication_date = None
        super(SensitiveArea, self).save(*args, **kwargs)

    @property
    def species_display(self):
        s = u'<a data-pk="%s" href="%s" title="%s">%s</a>' % (self.pk,
                                                              self.get_detail_url(),
                                                              self.species.name,
                                                              self.species.name)
        if self.published:
            s = u'<span class="badge badge-success" title="%s">&#x2606;</span> ' % _("Published") + s
        return s


Topology.add_property('sensitive_areas', lambda self: intersecting(SensitiveArea, self), _(u"Sensitive areas"))
Topology.add_property('published_sensitive_areas', lambda self: intersecting(SensitiveArea, self).filter(published=True), _(u"Published sensitive areas"))
