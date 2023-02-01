"""
   Sensitivity models
"""

import datetime
import simplekml
import logging
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.utils.translation import pgettext_lazy, gettext_lazy as _

from mapentity.serializers import plain_text
from pyopenair.factory import wkt2openair

from geotrek.authent.models import StructureRelated
from geotrek.common.mixins.models import (OptionalPictogramMixin, NoDeleteMixin, TimeStampedModelMixin,
                                          AddPropertyMixin, GeotrekMapEntityMixin, get_uuid_duplication)
from geotrek.common.utils import intersecting, classproperty
from geotrek.sensitivity.managers import SensitiveAreaManager
from geotrek.sensitivity.helpers import openair_atimes_concat
from geotrek.core.models import simplify_coords

logger = logging.getLogger("geotrek")

class SportPractice(TimeStampedModelMixin, models.Model):
    name = models.CharField(max_length=250, verbose_name=_("Name"))

    class Meta:
        ordering = ['name']
        verbose_name = _("Sport practice")
        verbose_name_plural = _("Sport practices")

    def __str__(self):
        return self.name


class Species(TimeStampedModelMixin, OptionalPictogramMixin):
    SPECIES = 1
    REGULATORY = 2

    name = models.CharField(max_length=250, verbose_name=_("Name"))
    # TODO: we should replace these 12 fields by a unique JSONField
    period01 = models.BooleanField(default=False, verbose_name=_("January"))
    period02 = models.BooleanField(default=False, verbose_name=_("February"))
    period03 = models.BooleanField(default=False, verbose_name=_("March"))
    period04 = models.BooleanField(default=False, verbose_name=_("April"))
    period05 = models.BooleanField(default=False, verbose_name=_("May"))
    period06 = models.BooleanField(default=False, verbose_name=_("June"))
    period07 = models.BooleanField(default=False, verbose_name=_("July"))
    period08 = models.BooleanField(default=False, verbose_name=_("August"))
    period09 = models.BooleanField(default=False, verbose_name=_("September"))
    period10 = models.BooleanField(default=False, verbose_name=_("October"))
    period11 = models.BooleanField(default=False, verbose_name=_("November"))
    period12 = models.BooleanField(default=False, verbose_name=_("Decembre"))
    practices = models.ManyToManyField(SportPractice, verbose_name=_("Sport practices"))
    url = models.URLField(blank=True, verbose_name="URL")
    radius = models.IntegerField(blank=True, null=True, verbose_name=_("Bubble radius"), help_text=_("meters"))
    category = models.IntegerField(verbose_name=_("Category"), editable=False, default=SPECIES,
                                   choices=((SPECIES, pgettext_lazy("Singular", "Species")),
                                            (REGULATORY, _("Regulatory"))))
    eid = models.CharField(verbose_name=_("External id"), max_length=1024, blank=True, null=True)

    class Meta:
        ordering = ['name']
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


class SensitiveArea(GeotrekMapEntityMixin, StructureRelated, TimeStampedModelMixin, NoDeleteMixin,
                    AddPropertyMixin):
    geom = models.GeometryField(srid=settings.SRID)
    geom_buffered = models.GeometryField(srid=settings.SRID, editable=False)
    species = models.ForeignKey(Species, verbose_name=_("Species or regulatory area"), on_delete=models.PROTECT)
    published = models.BooleanField(verbose_name=_("Published"), default=False, help_text=_("Visible on Geotrek-rando"))
    publication_date = models.DateField(verbose_name=_("Publication date"), null=True, blank=True, editable=False)
    description = models.TextField(verbose_name=_("Description"), blank=True)
    contact = models.TextField(verbose_name=_("Contact"), blank=True)
    eid = models.CharField(verbose_name=_("External id"), max_length=1024, blank=True, null=True)
    provider = models.CharField(verbose_name=_("Provider"), db_index=True, max_length=1024, blank=True)

    objects = SensitiveAreaManager()

    elements_duplication = {
        "attachments": {"uuid": get_uuid_duplication}
    }

    class Meta:
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

    def reload(self):
        """
        Reload into instance all computed attributes in triggers.
        """
        if self.pk:
            # Update computed values
            fromdb = self.__class__.objects.get(pk=self.pk)
            self.geom_buffered = fromdb.geom_buffered
        return self

    def save(self, *args, **kwargs):
        if self.publication_date is None and self.published:
            self.publication_date = datetime.date.today()
        if self.publication_date is not None and not self.published:
            self.publication_date = None
        super().save(*args, **kwargs)
        self.reload()

    @property
    def any_published(self):
        return self.published

    @property
    def published_status(self):
        """Returns the publication status by language.
        """
        status = []
        for language in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']:
            status.append({
                'lang': language[0],
                'language': language[1],
                'status': self.published
            })
        return status

    @property
    def published_langs(self):
        """Returns languages in which the object is published.
        """
        if self.published:
            return [language[0] for language in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']]
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
        if self.species.radius:
            geometry = ()
            for coords in geom.coords[0]:
                coords += (self.species.radius, )
                geometry += (coords, )
            geom = GEOSGeometry(Polygon(geometry), srid=settings.SRID)
        geom = geom.transform(4326, clone=True)  # KML uses WGS84
        line = kml.newpolygon(name=self.species.name,
                              description=plain_text(self.description),
                              altitudemode=simplekml.AltitudeMode.relativetoground,
                              outerboundaryis=simplify_coords(geom.coords[0]))
        line.style.linestyle.color = simplekml.Color.red  # Red
        line.style.linestyle.width = 4  # pixels
        return kml.kml()

    def openair(self):
        """Exports sensitivearea into OpenAir format"""
        geom = self.geom
        if geom.geom_type == 'Point':
            geom = geom.buffer(self.species.radius or settings.SENSITIVITY_DEFAULT_RADIUS, 4)
        geom = geom.transform(4326, clone=True)
        geom = geom.simplify(0.001, preserve_topology=True)
        other = {}
        other['*AUID'] = "GUId=! UId=! Id=(Identifiant-GeoTrek-sentivity){{{{{id}}}}}".format(id=str(self.pk))
        other['*ADescr'] = "{name} (published on {published_date})".format(name=self.species.name, published_date=self.publication_date.strftime("%d/%m/%Y"))
        other['*ATimes'] = openair_atimes_concat(self)
        wkt = geom.wkt
        data = {
            'wkt' : wkt, 
            'an': self.species.name, 
            'ac': 'ZSM', 
            'ah_unit':'m', 
            'ah_alti': self.species.radius or settings.SENSITIVITY_DEFAULT_RADIUS, 
            'ah_mode':'AGL', 
            'al_mode':'SFC', 
            # 'comment': self.species.name + ' (published on '+self.publication_date.strftime("%d/%m/%Y")+')',
            'other': other 
        }
        return wkt2openair(**data)

    @property
    def wgs84_geom(self):
        geom = self.geom
        if geom.geom_type == 'Point':
            geom = geom.buffer(self.species.radius or settings.SENSITIVITY_DEFAULT_RADIUS, 4)
        if self.species.radius:
            geometry = ()
            for coords in geom.coords[0]:
                coords += (self.species.radius, )
                geometry += (coords, )
            geom = GEOSGeometry(Polygon(geometry), srid=settings.SRID)
        geom = geom.transform(4326, clone=True)  # KML uses WGS84
        return geom

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

    Topology.add_property('sensitive_areas', lambda self: intersecting(SensitiveArea, self, distance=0, ordering=False,
                                                                       field='geom_buffered').select_related('species'),
                          _("Sensitive areas"))
    Topology.add_property('published_sensitive_areas',
                          lambda self: intersecting(SensitiveArea, self, distance=0, ordering=False,
                                                    field='geom_buffered').filter(published=True),
                          _("Published sensitive areas"))

if 'geotrek.trekking' in settings.INSTALLED_APPS:
    from geotrek.trekking import models as trekking_models

    SensitiveArea.add_property('pois', lambda self: intersecting(trekking_models.POI, self, 0), _("POIs"))
    SensitiveArea.add_property('treks', lambda self: intersecting(trekking_models.Trek, self, 0), _("Treks"))
    SensitiveArea.add_property('services', lambda self: intersecting(trekking_models.Service, self, 0), _("Services"))

if 'geotrek.diving' in settings.INSTALLED_APPS:
    from geotrek.diving.models import Dive

    Dive.add_property('sensitive_areas',
                      lambda self: intersecting(SensitiveArea, self, distance=0, ordering=False, field='geom_buffered'),
                      _("Sensitive areas"))
    Dive.add_property('published_sensitive_areas',
                      lambda self: intersecting(SensitiveArea, self, distance=0, ordering=False,
                                                field='geom_buffered').filter(published=True),
                      _("Published sensitive areas"))
    SensitiveArea.add_property('dives', lambda self: intersecting(Dive, self, 0), _("Dives"))
    SensitiveArea.add_property('published_dives',
                               lambda self: intersecting(Dive, self, 0).filter(published=True),
                               _("Published dives"))

if 'geotrek.tourism' in settings.INSTALLED_APPS:
    from geotrek.tourism import models as tourism_models

    tourism_models.TouristicContent.add_property('sensitive_areas',
                                                 lambda self: intersecting(SensitiveArea, self, distance=0,
                                                                           ordering=False, field='geom_buffered'),
                                                 _("Sensitive areas"))
    tourism_models.TouristicContent.add_property('published_sensitive_areas',
                                                 lambda self: intersecting(SensitiveArea, self, distance=0,
                                                                           ordering=False,
                                                                           field='geom_buffered').filter(
                                                     published=True), _("Published sensitive areas"))
    tourism_models.TouristicEvent.add_property('sensitive_areas',
                                               lambda self: intersecting(SensitiveArea, self, distance=0,
                                                                         ordering=False, field='geom_buffered'),
                                               _("Sensitive areas"))
    tourism_models.TouristicEvent.add_property('published_sensitive_areas',
                                               lambda self: intersecting(SensitiveArea, self, distance=0,
                                                                         ordering=False, field='geom_buffered').filter(
                                                   published=True), _("Published sensitive areas"))

    SensitiveArea.add_property('touristic_contents',
                               lambda self: intersecting(tourism_models.TouristicContent, self, 0),
                               _("Touristic contents"))
    SensitiveArea.add_property('published_touristic_contents',
                               lambda self: intersecting(tourism_models.TouristicContent, self, 0).filter(
                                   published=True),
                               _("Published touristic contents"))
    SensitiveArea.add_property('touristic_events', lambda self: intersecting(tourism_models.TouristicEvent, self, 0),
                               _("Touristic events"))
    SensitiveArea.add_property('published_touristic_events',
                               lambda self: intersecting(tourism_models.TouristicEvent, self, 0).filter(published=True),
                               _("Published touristic events"))

SensitiveArea.add_property('sensitive_areas', lambda self: intersecting(SensitiveArea, self, 0), _("Sensitive areas"))
SensitiveArea.add_property('published_sensitive_areas',
                           lambda self: intersecting(SensitiveArea, self, 0).filter(published=True),
                           _("Published sensitive areas"))
