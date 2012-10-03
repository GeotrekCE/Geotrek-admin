from HTMLParser import HTMLParser

from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.utils.html import strip_tags

import simplekml

from caminae.mapentity.models import MapEntityMixin
from caminae.core.models import TopologyMixin
from caminae.land.models import DistrictEdge
from caminae.common.utils import elevation_profile


class Trek(MapEntityMixin, TopologyMixin):

    name = models.CharField(verbose_name=_(u"Name"), max_length=128)
    departure = models.CharField(verbose_name=_(u"Departure"), max_length=128)
    arrival = models.CharField(verbose_name=_(u"Arrival"), max_length=128)
    published = models.BooleanField(verbose_name=_(u"Published"))

    ascent = models.IntegerField(editable=False, default=0, verbose_name=_(u"Ascent"))
    descent = models.IntegerField(editable=False, default=0, verbose_name=_(u"Descent"))
    min_elevation = models.IntegerField(editable=False, default=0, verbose_name=_(u"Minimum elevation"))
    max_elevation = models.IntegerField(editable=False, default=0, verbose_name=_(u"Maximum elevation"))

    description_teaser = models.TextField(verbose_name=_(u"Description teaser"))
    description = models.TextField(verbose_name=_(u"Description"))
    ambiance = models.TextField(verbose_name=_(u"Ambiance"))
    disabled_infrastructure = models.TextField(verbose_name=_(u"Handicapped's infrastructure"))
    duration = models.IntegerField(verbose_name=_(u"duration")) # in minutes

    is_park_centered = models.BooleanField(verbose_name=_(u"Is in the midst of the park"))
    is_transborder = models.BooleanField(verbose_name=_(u"Is transborder"))

    advised_parking = models.CharField(verbose_name=_(u"Advised parking"), max_length=128)
    parking_location = models.PointField(srid=settings.SRID, spatial_index=False)

    public_transport = models.TextField(verbose_name=_(u"Public transport"))
    advice = models.TextField(verbose_name=_(u"Advice"))

    themes = models.ManyToManyField('Theme', related_name="treks",
            verbose_name=_(u"Themes"))

    main_themes = models.ManyToManyField('Theme', related_name="treks_main",
            verbose_name=_(u"Main themes"))

    networks = models.ManyToManyField('TrekNetwork', related_name="treks",
            verbose_name=_(u"Trek networks"))

    usages = models.ManyToManyField('Usage', related_name="treks",
            verbose_name=_(u"Usages"))

    route = models.ForeignKey('Route', related_name='treks', null=True, blank=True,
            verbose_name=_(u"Route"))

    difficulty = models.ForeignKey('DifficultyLevel', related_name='treks', null=True, blank=True,
            verbose_name=_(u"Difficulty level"))

    destination = models.ForeignKey('Destination', related_name='treks', null=True, blank=True,
            verbose_name=_(u"Destination"))

    web_links = models.ManyToManyField('WebLink', related_name="treks",
            verbose_name=_(u"Web links"))

    # Override default manager
    objects = TopologyMixin.get_manager_cls(models.GeoManager)()

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
                  for t in a.path.topologymixin_set.existing().filter(
                      kind=POI.KIND,
                      aggregations__start_position__gte=a.start_position,
                      aggregations__end_position__lte=a.end_position
                  )]
        return POI.objects.filter(pk__in=[p.pk for p in s])

    @property
    def districts(self):
        s = []
        for a in self.aggregations.all():
            s += [DistrictEdge.objects.get(pk=t.pk).district
                  for t in a.path.topologymixin_set.existing().filter(
                      kind=DistrictEdge.KIND,
                      aggregations__start_position__lte=a.end_position,
                      aggregations__end_position__gte=a.start_position
                  )]
        return list(set(s))

    @property
    def poi_types(self):
        types = [p.type for p in self.pois]
        return set(types)

    @property
    def serializable_difficulty(self):
        return {'id': self.difficulty.pk,
                'label': self.difficulty.difficulty}

    @property
    def serializable_themes(self):
        return [{'id': t.pk,
                 'label': t.label,
                 'pictogram': t.pictogram.read().encode('base64')
                } for t in self.themes.all()]

    @property
    def serializable_usages(self):
        return [{'id': u.pk,
                 'label': u.usage} for u in self.usages.all()]

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

    class Meta:
        db_table = 'usages'

    def __unicode__(self):
        return self.usage


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


class Destination(models.Model):

    destination = models.CharField(verbose_name=_(u"Name"), max_length=128)
    pictogram = models.FileField(verbose_name=_(u"Pictogram"), upload_to=settings.UPLOAD_DIR)

    class Meta:
        db_table = 'destination'
        verbose_name = _(u"Destination")
        verbose_name_plural = _(u"Destinations")

    def __unicode__(self):
        return self.destination


class WebLink(models.Model):

    name = models.CharField(verbose_name=_(u"Name"), max_length=128)
    url = models.URLField(verbose_name=_(u"URL"), max_length=128)
    thumbnail = models.FileField(null=True, blank=True, verbose_name=_(u"Thumbnail"), upload_to=settings.UPLOAD_DIR)

    class Meta:
        db_table = 'liens_web'
        verbose_name = _(u"Web link")
        verbose_name_plural = _(u"Web links")

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.url)

    @classmethod
    @models.permalink
    def get_add_url(cls):
        return ('trekking:weblink_add', )


class Theme(models.Model):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128)
    pictogram = models.FileField(verbose_name=_(u"Pictogram"), upload_to=settings.UPLOAD_DIR)

    def __unicode__(self):
        return self.label


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



class POI(MapEntityMixin, TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True,
                                       db_column='evenement')
    name = models.CharField(verbose_name=_(u"Name"), max_length=128)
    description = models.TextField(verbose_name=_(u"Description"))
    type = models.ForeignKey('POIType', related_name='pois', verbose_name=_(u"Type"))

    # Override default manager
    objects = TopologyMixin.get_manager_cls(models.GeoManager)()

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
    def treks(self):
        s = []
        for a in self.aggregations.all():
            s += [Trek.objects.get(pk=t.pk)
                  for t in a.path.topologymixin_set.existing().filter(
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
