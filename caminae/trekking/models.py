from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from caminae.core.models import MapEntityMixin
from caminae.core.models import Path


class Trek(MapEntityMixin, models.Model):

    name = models.CharField(verbose_name=_(u"Name"), max_length=128)
    departure = models.CharField(verbose_name=_(u"Departure"), max_length=128)
    arrival = models.CharField(verbose_name=_(u"Arrival"), max_length=128)
    validated = models.BooleanField(verbose_name=_(u"Validated"))

    # same fields and core.models.path
    length = models.FloatField(verbose_name=_(u"Length"))
    ascent = models.IntegerField(editable=False, default=0, verbose_name=_(u"Ascent"))
    descent = models.IntegerField(editable=False, default=0, verbose_name=_(u"Descent"))
    min_elevation = models.IntegerField(editable=False, default=0, verbose_name=_(u"Minimum elevation"))
    max_elevation = models.IntegerField(editable=False, default=0, verbose_name=_(u"Maximum elevation"))

    description_teaser = models.TextField(verbose_name=_(u"Description teaser"))
    description = models.TextField(verbose_name=_(u"Description"))
    ambiance = models.TextField(verbose_name=_(u"Ambiance"))
    handicapped_infrastructure = models.TextField(verbose_name=_(u"Handicapped's infrastructure"))
    duration = models.IntegerField(verbose_name=_(u"duration")) # in minutes

    is_park_centered = models.BooleanField(verbose_name=_(u"Is in the midst of the park"))
    is_transborder = models.BooleanField(verbose_name=_(u"Is transborder"))

    advised_parking = models.CharField(verbose_name=_(u"Advised parking"), max_length=128)
    parking_location = models.PointField(editable=False, srid=settings.SRID, spatial_index=False)

    public_transport = models.TextField(verbose_name=_(u"Public transport"))
    advice = models.TextField(verbose_name=_(u"Advice"))

    geom = models.LineStringField(editable=False, srid=settings.SRID,
                                          spatial_index=False, dim=3)

    date_insert = models.DateTimeField(verbose_name=_(u"Insertion date"), auto_now_add=True)
    date_update = models.DateTimeField(verbose_name=_(u"Update date"), auto_now=True)
    deleted = models.BooleanField(verbose_name=_(u"Deleted"))


    networks = models.ManyToManyField('TrekNetwork', related_name="treks",
            verbose_name=_(u"Trek networks"))

    paths = models.ManyToManyField(Path, related_name="treks",
            verbose_name=_(u"Paths composition"))

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

    # missing: photo

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
    url = models.URLField(verbose_name=_(u"Name"), max_length=128)
    thumbnail = models.FileField(verbose_name=_(u"Thumbnail"), upload_to=settings.UPLOAD_DIR)

    class Meta:
        db_table = 'liens_web'
        verbose_name = _(u"Web link")
        verbose_name_plural = _(u"Web links")

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.url)



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


# TODO: need to define "attached files" in the MCD to complete this model
# class Photos(models.Model):
#     pass
#
#     class Meta:
#         db_table = 'photos'
