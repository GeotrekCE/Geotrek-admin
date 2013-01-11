import logging
import mimetypes
from HTMLParser import HTMLParser

from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.utils.html import strip_tags

import simplekml

from caminae.mapentity.models import MapEntityMixin
from caminae.core.models import Topology
from caminae.common.utils import elevation_profile


logger = logging.getLogger(__name__)


class Trek(MapEntityMixin, Topology):

    name = models.CharField(verbose_name=_(u"Name"), max_length=128)
    departure = models.CharField(verbose_name=_(u"Departure"), max_length=128, blank=True)
    arrival = models.CharField(verbose_name=_(u"Arrival"), max_length=128, blank=True)
    published = models.BooleanField(verbose_name=_(u"Published"))

    ascent = models.IntegerField(editable=False, default=0, verbose_name=_(u"Ascent"))
    descent = models.IntegerField(editable=False, default=0, verbose_name=_(u"Descent"))
    min_elevation = models.IntegerField(editable=False, default=0, verbose_name=_(u"Minimum elevation"))
    max_elevation = models.IntegerField(editable=False, default=0, verbose_name=_(u"Maximum elevation"))

    description_teaser = models.TextField(verbose_name=_(u"Description teaser"), blank=True)
    description = models.TextField(verbose_name=_(u"Description"), blank=True)
    ambiance = models.TextField(verbose_name=_(u"Ambiance"), blank=True)
    access = models.TextField(verbose_name=_(u"Access"), blank=True)
    disabled_infrastructure = models.TextField(verbose_name=_(u"Handicapped's infrastructure"))
    duration = models.IntegerField(verbose_name=_(u"duration"), blank=True, null=True) # in minutes

    is_park_centered = models.BooleanField(verbose_name=_(u"Is in the midst of the park"))

    advised_parking = models.CharField(verbose_name=_(u"Advised parking"), max_length=128, blank=True)
    parking_location = models.PointField(srid=settings.SRID, spatial_index=False, blank=True, null=True)

    public_transport = models.TextField(verbose_name=_(u"Public transport"), blank=True)
    advice = models.TextField(verbose_name=_(u"Advice"), blank=True)

    themes = models.ManyToManyField('Theme', related_name="treks",
            blank=True, null=True, verbose_name=_(u"Themes"))

    networks = models.ManyToManyField('TrekNetwork', related_name="treks",
            blank=True, null=True, verbose_name=_(u"Trek networks"))

    usages = models.ManyToManyField('Usage', related_name="treks",
            blank=True, null=True, verbose_name=_(u"Usages"))

    route = models.ForeignKey('Route', related_name='treks',
            blank=True, null=True, verbose_name=_(u"Route"))

    difficulty = models.ForeignKey('DifficultyLevel', related_name='treks',
            blank=True, null=True, verbose_name=_(u"Difficulty level"))

    web_links = models.ManyToManyField('WebLink', related_name="treks",
            blank=True, null=True, verbose_name=_(u"Web links"))

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    ## relationships helpers ##
    # TODO: can not be have an intermediary table and be "symmetrical" at the same time
    # trek_relationships = models.ManyToManyField("self", through="TrekRelationship", symmetrical=True)
    def get_relationships(self):
        return TrekRelationship.objects.relationships(self)

    def get_related_treks_values(self):
        return TrekRelationship.objects.related_treks_values(self)

    class Meta:
        db_table = 'itineraire'
        verbose_name = _(u"Trek")
        verbose_name_plural = _(u"Treks")

    @property
    def pois(self):
        s = []
        for a in self.aggregations.all():
            s += [POI.objects.get(pk=t.pk)
                  for t in a.path.topology_set.existing().filter(
                      kind=POI.KIND,
                      aggregations__start_position__gte=a.start_position,
                      aggregations__end_position__lte=a.end_position
                  )]
        return POI.objects.filter(pk__in=[p.pk for p in s])

    @property
    def poi_types(self):
        types = [p.type for p in self.pois]
        return set(types)

    @property
    def serializable_difficulty(self):
        if not self.difficulty:
            return None
        return {'id': self.difficulty.pk,
                'label': self.difficulty.difficulty}

    @property
    def serializable_themes(self):
        return [{'id': t.pk,
                 'label': t.label,
                } for t in self.themes.all()]

    @property
    def serializable_usages(self):
        return [{'id': u.pk,
                 'label': u.usage} for u in self.usages.all()]

    @property
    def serializable_districts(self):
        return [{'id': d.pk,
                 'name': d.name} for d in self.districts]

    @property
    def serializable_weblinks(self):
        return [{'id': w.pk,
                 'name': w.name,
                 'url': w.url} for w in self.web_links.all()]

    @property
    def serializable_parking_location(self):
        if not self.parking_location:
            return None
        return self.parking_location.transform(settings.API_SRID, clone=True).coords

    @property
    def elevation_profile(self):
        return elevation_profile(self.geom)

    @property
    def is_loop(self):
        return self.departure == self.arrival

    @property
    def name_display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (self.pk, self.get_detail_url(), self.name)

    @property
    def name_csv_display(self):
        return unicode(self.name)

    def kml(self):
        """ Exports trek into KML format, add geometry as linestring and POI
        as place marks """
        html = HTMLParser()
        kml = simplekml.Kml()
        # Main itinerary
        kml.newlinestring(name=self.name,
                          description=html.unescape(strip_tags(self.description)),
                          coords=self.geom.coords)
        # Place marks
        for poi in self.pois:
            place = poi.geom_as_point()
            place.transform(settings.API_SRID)
            kml.newpoint(name=poi.name,
                         description=html.unescape(strip_tags(poi.description)),
                         coords=[place.coords])
        return kml._genkml()

    def __unicode__(self):
        return u"%s (%s - %s)" % (self.name, self.departure, self.arrival)


class TrekNetwork(models.Model):

    network = models.CharField(verbose_name=_(u"Name"), max_length=128)

    class Meta:
        db_table = 'reseau'
        verbose_name = _(u"Trek network")
        verbose_name_plural = _(u"Trek networks")

    def __unicode__(self):
        return self.network


class Usage(models.Model):

    usage = models.CharField(verbose_name=_(u"Name"), max_length=128)
    pictogram = models.FileField(verbose_name=_(u"Pictogram"), upload_to=settings.UPLOAD_DIR)

    class Meta:
        db_table = 'usages'

    def __unicode__(self):
        return self.usage

    def pictogram_img(self):
        return u'<img src="%s" />' % (self.pictogram.url if self.pictogram else "")
    pictogram_img.short_description = _("Pictogram")
    pictogram_img.allow_tags = True


class Route(models.Model):

    route = models.CharField(verbose_name=_(u"Name"), max_length=128)

    class Meta:
        db_table = 'parcours'
        verbose_name = _(u"Route")
        verbose_name_plural = _(u"Routes")

    def __unicode__(self):
        return self.route


class DifficultyLevel(models.Model):

    difficulty = models.CharField(verbose_name=_(u"Difficulty level"), max_length=128)

    class Meta:
        db_table = 'classement_difficulte'
        verbose_name = _(u"Difficulty level")
        verbose_name_plural = _(u"Difficulty levels")

    def __unicode__(self):
        return self.difficulty


class WebLinkManager(models.Manager):
    def get_query_set(self):
        return super(WebLinkManager, self).get_query_set().select_related('category')


class WebLink(models.Model):

    name = models.CharField(verbose_name=_(u"Name"), max_length=128)
    url = models.URLField(verbose_name=_(u"URL"), max_length=128)
    category = models.ForeignKey('WebLinkCategory', verbose_name=_(u"Category"),
                                 related_name='links', null=True, blank=True)

    objects = WebLinkManager()

    class Meta:
        db_table = 'liens_web'
        verbose_name = _(u"Web link")
        verbose_name_plural = _(u"Web links")

    def __unicode__(self):
        category =  "%s - " % self.category.label if self.category else ""
        return u"%s%s (%s)" % (category, self.name, self.url)

    @classmethod
    @models.permalink
    def get_add_url(cls):
        return ('trekking:weblink_add', )


class WebLinkCategory(models.Model):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128)
    pictogram = models.FileField(verbose_name=_(u"Pictogram"), upload_to=settings.UPLOAD_DIR)

    class Meta:
        db_table = 'o_t_web_category'
        verbose_name = _(u"Web link category")
        verbose_name_plural = _(u"Web link categories")

    def __unicode__(self):
        return u"%s" % self.label

    def pictogram_img(self):
        return u'<img src="%s" />' % (self.pictogram.url if self.pictogram else "")
    pictogram_img.short_description = _("Pictogram")
    pictogram_img.allow_tags = True


class Theme(models.Model):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128)
    pictogram = models.FileField(verbose_name=_(u"Pictogram"), upload_to=settings.UPLOAD_DIR)

    def __unicode__(self):
        return self.label

    def pictogram_img(self):
        return u'<img src="%s" />' % (self.pictogram.url if self.pictogram else "")
    pictogram_img.short_description = _("Pictogram")
    pictogram_img.allow_tags = True


class TrekRelationshipManager(models.Manager):

    def relationships(self, trek):
        """Ease the request to know all relationship of a given trek:

            trek_1 = Trek.objects.get(pk=42)
            TrekRelationship.objects.relationships(trek_1)
        """
        qs = super(TrekRelationshipManager, self).get_query_set()
        return qs.filter(Q(trek_a=trek) | Q(trek_b=trek))

    def related_treks_values(self, trek):
        """
        Returns related treks of a trek as an Array (and not a queryset !).
        """
        rss = self.relationships(trek)
        return [ rs.trek_b if rs.trek_a == trek else rs.trek_a for rs in rss ]


# TODO: can not be have an intermediary table and be "symmetrical" at the same time
# We would like to use it disregarding intervention is in _a or _b:
#
#     trek1.save()
#     trek2.save()
#     rs = TrekRelationship.objects.create(trek_a=trek1, trek_b=trek2, ...)
#
#     trek1.relationships()
#     trek2.relationships()
class TrekRelationship(models.Model):

    has_common_departure = models.BooleanField(verbose_name=_(u"Common departure"))
    has_common_edge = models.BooleanField(verbose_name=_(u"Common edge"))
    is_circuit_step = models.BooleanField(verbose_name=_(u"Circuit step"))

    trek_a = models.ForeignKey(Trek, related_name="trek_relationship_a")
    trek_b = models.ForeignKey(Trek, related_name="trek_relationship_b")

    class Meta:
        db_table = 'liens_itineraire'
        verbose_name = _(u"Trek relationship")
        verbose_name_plural = _(u"Trek relationships")
        # Not sufficient we should ensure
        # we don't get (trek_a, trek_b) and (trek_b, trek_a)
        unique_together = (('trek_a', 'trek_b'), )

    objects = TrekRelationshipManager()



class POI(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    name = models.CharField(verbose_name=_(u"Name"), max_length=128)
    description = models.TextField(verbose_name=_(u"Description"))
    type = models.ForeignKey('POIType', related_name='pois', verbose_name=_(u"Type"))

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    def __unicode__(self):
        return self.name

    @property
    def type_display(self):
        return unicode(self.type)

    @property
    def name_display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (self.pk, self.get_detail_url(), self.name)

    @property
    def name_csv_display(self):
        return unicode(self.name)

    @property
    def serializable_type(self):
        return {'label': self.type.label,
                'pictogram': self.type.serializable_pictogram}

    @property
    def treks(self):
        s = []
        for a in self.aggregations.all():
            s += [Trek.objects.get(pk=t.pk)
                  for t in a.path.topology_set.existing().filter(
                      kind=Trek.KIND,
                      aggregations__start_position__lte=a.end_position,
                      aggregations__end_position__gte=a.start_position
                  )]
        return list(set(s))


class POIType(models.Model):
    label = models.CharField(verbose_name=_(u"Label"), max_length=128)
    pictogram = models.FileField(verbose_name=_(u"Pictogram"), upload_to=settings.UPLOAD_DIR)

    def __unicode__(self):
        return self.label

    @property
    def serializable_pictogram(self):
        try:
            pictopath = self.pictogram.name
            mimetype = mimetypes.guess_type(pictopath)
            mimetype = mimetype[0] if mimetype else 'application/octet-stream'
            encoded = self.pictogram.read().encode('base64').replace("\n", '')
            return "%s;base64,%s" % (mimetype, encoded)
        except (IOError, ValueError), e:
            logger.warning(e)
            return ''
