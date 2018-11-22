"""
   Sensitivity models
"""

import datetime
import simplekml

from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import pgettext_lazy, ugettext_lazy as _
from mapentity.models import MapEntityMixin
from mapentity.serializers import plain_text
from geotrek.authent.models import StructureRelated
from geotrek.common.mixins import (OptionalPictogramMixin, NoDeleteMixin, TimeStampedModelMixin, AddPropertyMixin)
from geotrek.common.utils import intersecting, classproperty


class SportPractice(models.Model):
    name = models.CharField(max_length=250, db_column='nom', verbose_name=_("Name"))

    class Meta:
        ordering = ['name']
        db_table = 's_b_pratique_sportive'
        verbose_name = _("Sport practice")
        verbose_name_plural = _("Sport practices")

    def __str__(self):
        return self.name


class Species(OptionalPictogramMixin):
    SPECIES = 1
    REGULATORY = 2

    name = models.CharField(max_length=250, db_column='nom', verbose_name=_("Name"))
    period01 = models.BooleanField(default=False, db_column='periode01', verbose_name=_("January"))
    period02 = models.BooleanField(default=False, db_column='periode02', verbose_name=_("February"))
    period03 = models.BooleanField(default=False, db_column='periode03', verbose_name=_("March"))
    period04 = models.BooleanField(default=False, db_column='periode04', verbose_name=_("April"))
    period05 = models.BooleanField(default=False, db_column='periode05', verbose_name=_("May"))
    period06 = models.BooleanField(default=False, db_column='periode06', verbose_name=_("June"))
    period07 = models.BooleanField(default=False, db_column='periode07', verbose_name=_("July"))
    period08 = models.BooleanField(default=False, db_column='periode08', verbose_name=_("August"))
    period09 = models.BooleanField(default=False, db_column='periode09', verbose_name=_("September"))
    period10 = models.BooleanField(default=False, db_column='periode10', verbose_name=_("October"))
    period11 = models.BooleanField(default=False, db_column='periode11', verbose_name=_("November"))
    period12 = models.BooleanField(default=False, db_column='periode12', verbose_name=_("Decembre"))
    practices = models.ManyToManyField(SportPractice, db_table='s_r_espece_pratique_sportive',
                                       verbose_name=_("Sport practices"))
    url = models.URLField(blank=True, verbose_name="URL")
    radius = models.IntegerField(db_column='rayon', blank=True, null=True, verbose_name=_("Bubble radius"),
                                 help_text=_("meters"))
    category = models.IntegerField(verbose_name=_("Category"), db_column='categorie', editable=False, default=SPECIES,
                                   choices=((SPECIES, pgettext_lazy("Singular", "Species")),
                                            (REGULATORY, _("Regulatory"))))
    eid = models.CharField(verbose_name=_("External id"), max_length=128, blank=True, null=True,
                           db_column='id_externe')

    class Meta:
        ordering = ['name']
        db_table = 's_b_espece_ou_suite_zone_regl'
        verbose_name = pgettext_lazy("Singular", "Species")
        verbose_name_plural = _("Species")

    def __str__(self):
        return self.name

    def pretty_period(self):
        return ", ".join([str(self._meta.get_field('period{:02}'.format(p)).verbose_name)
                         for p in range(1, 13)
                         if getattr(self, 'period{:02}'.format(p))])

    def pretty_practices(self):
        return ", ".join([str(practice) for practice in self.practices.all()])


class SensitiveArea(MapEntityMixin, StructureRelated, TimeStampedModelMixin, NoDeleteMixin,
                    AddPropertyMixin):
    geom = models.GeometryField(srid=settings.SRID)
    species = models.ForeignKey(Species, verbose_name=_("Sensitive area"), db_column='espece',
                                on_delete=models.PROTECT)
    published = models.BooleanField(verbose_name=_("Published"), default=False,
                                    help_text=_("Online"), db_column='public')
    publication_date = models.DateField(verbose_name=_("Publication date"),
                                        null=True, blank=True, editable=False,
                                        db_column='date_publication')
    description = models.TextField(verbose_name=_("Description"), blank=True)
    contact = models.TextField(verbose_name=_("Contact"), blank=True)
    eid = models.CharField(verbose_name=_("External id"), max_length=128, blank=True, null=True,
                           db_column='id_externe')

    objects = NoDeleteMixin.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 's_t_zone_sensible'
        verbose_name = _("Sensitive area")
        verbose_name_plural = _("Sensitive areas")
        permissions = (
            ("import_sensitivearea", "Can import Sensitive area"),
        )

    def __str__(self):
        return self.species.name

    @property
    def radius(self):
        if self.species.radius is None:
            return settings.SENSITIVITY_DEFAULT_RADIUS
        return self.species.radius

    @classproperty
    def radius_verbose_name(cls):
        return _("Radius")

    @property
    def category_display(self):
        return self.species.get_category_display()

    @classproperty
    def category_verbose_name(cls):
        return _("Category")

    def save(self, *args, **kwargs):
        if self.publication_date is None and self.published:
            self.publication_date = datetime.date.today()
        if self.publication_date is not None and not self.published:
            self.publication_date = None
        super(SensitiveArea, self).save(*args, **kwargs)

    @property
    def any_published(self):
        return self.published

    @property
    def published_status(self):
        """Returns the publication status by language.
        """
        status = []
        for l in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']:
            status.append({
                'lang': l[0],
                'language': l[1],
                'status': self.published
            })
        return status

    @property
    def published_langs(self):
        """Returns languages in which the object is published.
        """
        if self.published:
            return [l[0] for l in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']]
        else:
            return []

    @property
    def species_display(self):
        s = '<a data-pk="%s" href="%s" title="%s">%s</a>' % (self.pk,
                                                             self.get_detail_url(),
                                                             self.species.name,
                                                             self.species.name)
        if self.published:
            s = '<span class="badge badge-success" title="%s">&#x2606;</span> ' % _("Published") + s
        return s

    @property
    def extent(self):
        return self.geom.transform(settings.API_SRID, clone=True).extent if self.geom else None

    def kml(self):
        """Exports sensitivearea into KML format"""
        kml = simplekml.Kml()
        geom = self.geom
        if geom.geom_type == 'Point':
            geom = geom.buffer(self.species.radius or settings.SENSITIVITY_DEFAULT_RADIUS, 4)
        geom = geom.transform(4326, clone=True)  # KML uses WGS84
        line = kml.newpolygon(name=self.species.name,
                              description=plain_text(self.description),
                              outerboundaryis=geom.coords[0])
        line.style.linestyle.color = simplekml.Color.red  # Red
        line.style.linestyle.width = 4  # pixels
        return kml.kml()

    def is_public(self):
        return self.published

    @property
    def pretty_period(self):
        return self.species.pretty_period()
    pretty_period_verbose_name = _("Period")

    @property
    def pretty_practices(self):
        return self.species.pretty_practices()
    pretty_practices_verbose_name = _("Practices")


if 'geotrek.core' in settings.INSTALLED_APPS:
    from geotrek.core.models import Topology
    Topology.add_property('sensitive_areas', lambda self: intersecting(SensitiveArea, self, settings.SENSITIVE_AREA_INTERSECTION_MARGIN), _("Sensitive areas"))
    Topology.add_property('published_sensitive_areas', lambda self: intersecting(SensitiveArea, self, settings.SENSITIVE_AREA_INTERSECTION_MARGIN).filter(published=True), _("Published sensitive areas"))
