import os
import logging
from HTMLParser import HTMLParser
import shutil

from django.conf import settings
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.template.defaultfilters import slugify
from easy_thumbnails.alias import aliases
from easy_thumbnails.files import get_thumbnailer

import simplekml
from PIL import Image

from caminae.mapentity.models import MapEntityMixin
from caminae.core.models import Path, Topology
from caminae.common.utils import elevation_profile, classproperty
from caminae.maintenance.models import Intervention, Project

logger = logging.getLogger(__name__)


class PicturesMixin(object):
    """A common class to share code between Trek and POI regarding
    attached pictures"""

    @property
    def pictures(self):
        """
        Find first image among attachments.
        """
        return [a for a in self.attachments.all() if a.is_image]

    @property
    def serializable_pictures(self):
        serialized = []
        for picture in self.pictures:
            thumbnailer = get_thumbnailer(picture.attachment_file)
            thdetail = thumbnailer.get_thumbnail(aliases.get('medium'))
            serialized.append({
                'author': picture.author,
                'title': picture.title,
                'legend': picture.legend,
                'url': os.path.join(settings.MEDIA_URL, thdetail.name)
            })
        return serialized

    @property
    def picture_print(self):
        for picture in self.pictures:
            thumbnailer = get_thumbnailer(picture.attachment_file)
            return thumbnailer.get_thumbnail(aliases.get('print'))
        return None

    @property
    def thumbnail(self):
        for picture in self.pictures:
            thumbnailer = get_thumbnailer(picture.attachment_file)
            return thumbnailer.get_thumbnail(aliases.get('small-square'))
        return None

    @classproperty
    def thumbnail_verbose_name(self):
        return _("Thumbnail")

    @property
    def thumbnail_display(self):
        thumbnail = self.thumbnail
        if thumbnail is None:
            return _("None")
        return '<img height="20" width="20" src="%s"/>' % os.path.join(settings.MEDIA_URL, thumbnail.name)

    @property
    def serializable_thumbnail(self):
        th = self.thumbnail
        if not th:
            return None
        return os.path.join(settings.MEDIA_URL, th.name)


class Trek(PicturesMixin, MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    name = models.CharField(verbose_name=_(u"Name"), max_length=128,
                            help_text=_(u"Public name (Change carefully)"), db_column='nom')
    departure = models.CharField(verbose_name=_(u"Departure"), max_length=128, blank=True,
                                 help_text=_(u"Departure description"), db_column='depart')
    arrival = models.CharField(verbose_name=_(u"Arrival"), max_length=128, blank=True,
                               help_text=_(u"Arrival description"), db_column='arrivee')
    published = models.BooleanField(verbose_name=_(u"Published"),
                                    help_text=_(u"Online"), db_column='public')
    description_teaser = models.TextField(verbose_name=_(u"Description teaser"), blank=True,
                                          help_text=_(u"A brief summary (map pop-ups)"), db_column='chapeau')
    description = models.TextField(verbose_name=_(u"Description"), blank=True, db_column='description',
                                   help_text=_(u"Complete description"))
    ambiance = models.TextField(verbose_name=_(u"Ambiance"), blank=True, db_column='ambiance',
                                help_text=_(u"Main attraction and interest"))
    access = models.TextField(verbose_name=_(u"Access"), blank=True, db_column='acces',
                              help_text=_(u"Best way to go"))
    disabled_infrastructure = models.TextField(verbose_name=_(u"Disabled infrastructure"), db_column='handicap',
                                               help_text=_(u"Any specific infrastructure"))
    duration = models.IntegerField(verbose_name=_(u"Duration"), default=0, blank=True, null=True, db_column='duree',
                                   help_text=_(u"In hours"))

    is_park_centered = models.BooleanField(verbose_name=_(u"Is in the midst of the park"), db_column='coeur',
                                           help_text=_(u"Crosses center of park"))

    advised_parking = models.CharField(verbose_name=_(u"Advised parking"), max_length=128, blank=True, db_column='parking',
                                       help_text=_(u"Where to park"))
    parking_location = models.PointField(srid=settings.SRID, spatial_index=False, blank=True, null=True, db_column='geom_parking')

    public_transport = models.TextField(verbose_name=_(u"Public transport"), blank=True, db_column='transport',
                                        help_text=_(u"Train, bus (see web links)"))
    advice = models.TextField(verbose_name=_(u"Advice"), blank=True, db_column='recommandation',
                              help_text=_(u"Risks, danger, best period, ..."))

    themes = models.ManyToManyField('Theme', related_name="treks",
                                    db_table="o_r_itineraire_theme", blank=True, null=True, verbose_name=_(u"Themes"))

    networks = models.ManyToManyField('TrekNetwork', related_name="treks",
                                      db_table="o_r_itineraire_reseau", blank=True, null=True, verbose_name=_(u"Networks"))

    usages = models.ManyToManyField('Usage', related_name="treks",
                                    db_table="o_r_itineraire_usage", blank=True, null=True, verbose_name=_(u"Usages"))

    route = models.ForeignKey('Route', related_name='treks',
                              blank=True, null=True, verbose_name=_(u"Route"), db_column='parcours')

    difficulty = models.ForeignKey('DifficultyLevel', related_name='treks',
                                   blank=True, null=True, verbose_name=_(u"Difficulty"), db_column='difficulte')

    web_links = models.ManyToManyField('WebLink', related_name="treks",
                                       db_table="o_r_itineraire_web", blank=True, null=True, verbose_name=_(u"Web links"))

    related_treks = models.ManyToManyField('self', through='TrekRelationship',
                                           verbose_name=_(u"Related treks"), symmetrical=False,
                                           related_name='related_treks+')  # Hide reverse attribute

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'o_t_itineraire'
        verbose_name = _(u"Trek")
        verbose_name_plural = _(u"Treks")

    @property
    def slug(self):
        return slugify(self.name)

    @models.permalink
    def get_document_public_url(self):
        return ('trekking:trek_document_public', [str(self.pk)])

    @models.permalink
    def get_document_public_poi_url(self):
        return ('trekking:trek_document_public_poi', [str(self.pk)])

    @property
    def related(self):
        return self.related_treks.exclude(deleted=True).exclude(pk=self.pk).distinct()

    @property
    def relationships(self):
        # Does not matter if a or b
        return TrekRelationship.objects.filter(trek_a=self)

    @property
    def pois(self):
        return POI.overlapping(Trek.objects.filter(pk=self))

    @property
    def poi_types(self):
        pks = set(self.pois.values_list('type', flat=True))
        return POIType.objects.filter(pk__in=pks)

    def prepare_map_image(self, rooturl):
        """
        We override the default behaviour of map image preparation :
        if the trek has a attached picture file with *title* ``mapimage``, we use it
        as a screenshot.

        Mainly because of BUG #282 : vectorial objects are offsetted on background.
        Seems to be a PhantomJS/CasperJS bug.
        TODO: remove this when ready ?
        """
        attached = None
        for picture in [a for a in self.attachments.all() if a.is_image]:
            if picture.title == 'mapimage':
                attached = picture.attachment_file
                break
        if attached is None:
            super(Trek, self).prepare_map_image(rooturl)
        else:
            # Copy it along other screenshots
            src = os.path.join(settings.MEDIA_ROOT, attached.name)
            dst = self.get_map_image_path()
            shutil.copyfile(src, dst)

    @property
    def pictures(self):
        """
        Override pictures list. See Trek.prepare_map_image()
        """
        return [a for a in self.attachments.all() if a.is_image and a.title != 'mapimage']

    @property
    def serializable_relationships(self):
        return [{
                'has_common_departure': rel.has_common_departure,
                'has_common_edge': rel.has_common_edge,
                'is_circuit_step': rel.is_circuit_step,
                'trek': {
                    'pk': rel.trek_b.pk,
                    'slug': rel.trek_b.slug,
                    'name': rel.trek_b.name,
                    'url': reverse('trekking:trek_json_detail', args=(rel.trek_b.pk,)),
                },
                'published': rel.trek_b.published} for rel in self.relationships]

    @property
    def serializable_cities(self):
        return [{'code': city.code,
                 'name': city.name} for city in self.cities]

    @property
    def serializable_networks(self):
        return [{'id': network.id,
                 'name': network.network} for network in self.networks.all()]

    @property
    def serializable_difficulty(self):
        if not self.difficulty:
            return None
        return {'id': self.difficulty.pk,
                'label': self.difficulty.difficulty}

    @property
    def serializable_themes(self):
        return [{'id': t.pk,
                 'pictogram': os.path.join(settings.MEDIA_URL, t.pictogram.name),
                 'label': t.label} for t in self.themes.all()]

    @property
    def serializable_usages(self):
        return [{'id': u.pk,
                 'pictogram': os.path.join(settings.MEDIA_URL, u.pictogram.name),
                 'label': u.usage} for u in self.usages.all()]

    @property
    def serializable_districts(self):
        return [{'id': d.pk,
                 'name': d.name} for d in self.districts]

    @property
    def serializable_route(self):
        if not self.route:
            return None
        return {'id': self.route.pk,
                'label': self.route.route}

    @property
    def serializable_web_links(self):
        return [{'id': w.pk,
                 'name': w.name,
                 'category': w.serializable_category,
                 'url': w.url} for w in self.web_links.all()]

    @property
    def serializable_parking_location(self):
        if not self.parking_location:
            return None
        return self.parking_location.transform(settings.API_SRID, clone=True).coords

    @property
    def elevation_profile(self):
        if not self.geom:
            return []
        return elevation_profile(self.geom, maxitems=settings.PROFILE_MAXSIZE)

    @property
    def name_display(self):
        s = u'<a data-pk="%s" href="%s" >%s</a>' % (self.pk, self.get_detail_url(), self.name)
        if self.published:
            s = u'<span class="badge badge-success">&#x2606;</span> ' + s
        return s

    @property
    def name_csv_display(self):
        return unicode(self.name)

    @property
    def networks_display(self):
        return ', '.join([unicode(n) for n in self.networks.all()])

    @property
    def themes_display(self):
        return ', '.join([unicode(n) for n in self.themes.all()])

    @property
    def usages_display(self):
        return ', '.join([unicode(n) for n in self.usages.all()])

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

    def is_complete(self):
        """It should also have a description, etc.
        """
        mandatory = ['departure', 'arrival', 'description_teaser']
        for f in mandatory:
            if not getattr(self, f):
                return False
        return True

    def has_geom_valid(self):
        """A trek should be a LineString, even if it's a loop.
        """
        return self.geom and self.geom.geom_type.lower() == 'linestring'

    def is_publishable(self):
        return self.is_complete() and self.has_geom_valid()

    def __unicode__(self):
        return u"%s (%s - %s)" % (self.name, self.departure, self.arrival)

    @classmethod
    def path_treks(cls, path):
        return cls.objects.existing().filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_treks(cls, topology):
        return cls.objects.existing().filter(aggregations__path__in=topology.paths.all()).distinct('pk')

Path.add_property('treks', lambda self: Trek.path_treks(self))
Topology.add_property('treks', lambda self: Trek.topology_treks(self))
Intervention.add_property('treks', lambda self: self.topology.treks if self.topology else [])
Project.add_property('treks', lambda self: self.edges_by_attr('treks'))


class TrekRelationshipManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        # Select treks foreign keys by default
        qs = super(TrekRelationshipManager, self).get_query_set().select_related('trek_a', 'trek_b')
        # Exclude deleted treks
        return qs.exclude(trek_a__deleted=True).exclude(trek_b__deleted=True)


class TrekRelationship(models.Model):
    """
    Relationships between treks : symmetrical aspect is managed by a trigger that
    duplicates all couples (trek_a, trek_b)
    """
    has_common_departure = models.BooleanField(verbose_name=_(u"Common departure"), db_column='depart_commun', default=False)
    has_common_edge = models.BooleanField(verbose_name=_(u"Common edge"), db_column='troncons_communs', default=False)
    is_circuit_step = models.BooleanField(verbose_name=_(u"Circuit step"), db_column='etape_circuit', default=False)

    trek_a = models.ForeignKey(Trek, related_name="trek_relationship_a", db_column='itineraire_a')
    trek_b = models.ForeignKey(Trek, related_name="trek_relationship_b", db_column='itineraire_b', verbose_name=_(u"Trek"))

    objects = TrekRelationshipManager()

    class Meta:
        db_table = 'o_r_itineraire_itineraire'
        verbose_name = _(u"Trek relationship")
        verbose_name_plural = _(u"Trek relationships")
        unique_together = ('trek_a', 'trek_b')

    def __unicode__(self):
        return u"%s <--> %s" % (self.trek_a, self.trek_b)


class TrekNetwork(models.Model):

    network = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='reseau')

    class Meta:
        db_table = 'o_b_reseau'
        verbose_name = _(u"Trek network")
        verbose_name_plural = _(u"Trek networks")
        ordering = ['network']

    def __unicode__(self):
        return self.network


class Usage(models.Model):

    usage = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='usage')
    pictogram = models.FileField(verbose_name=_(u"Pictogram"), upload_to=settings.UPLOAD_DIR,
                                 db_column='picto')

    class Meta:
        db_table = 'o_b_usage'
        ordering = ['usage']

    def __unicode__(self):
        return self.usage

    def pictogram_img(self):
        return u'<img src="%s" />' % (self.pictogram.url if self.pictogram else "")
    pictogram_img.short_description = _("Pictogram")
    pictogram_img.allow_tags = True


class Route(models.Model):

    route = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='parcours')

    class Meta:
        db_table = 'o_b_parcours'
        verbose_name = _(u"Route")
        verbose_name_plural = _(u"Routes")
        ordering = ['route']

    def __unicode__(self):
        return self.route


class DifficultyLevel(models.Model):

    difficulty = models.CharField(verbose_name=_(u"Difficulty level"),
                                  max_length=128, db_column='difficulte')

    class Meta:
        db_table = 'o_b_difficulte'
        verbose_name = _(u"Difficulty level")
        verbose_name_plural = _(u"Difficulty levels")
        ordering = ['id']

    def __unicode__(self):
        return self.difficulty


class WebLinkManager(models.Manager):
    def get_query_set(self):
        return super(WebLinkManager, self).get_query_set().select_related('category')


class WebLink(models.Model):

    name = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='nom')
    url = models.URLField(verbose_name=_(u"URL"), max_length=128, db_column='url')
    category = models.ForeignKey('WebLinkCategory', verbose_name=_(u"Category"),
                                 related_name='links', null=True, blank=True,
                                 db_column='categorie')

    objects = WebLinkManager()

    class Meta:
        db_table = 'o_t_web'
        verbose_name = _(u"Web link")
        verbose_name_plural = _(u"Web links")

    def __unicode__(self):
        category = "%s - " % self.category.label if self.category else ""
        return u"%s%s (%s)" % (category, self.name, self.url)

    @classmethod
    @models.permalink
    def get_add_url(cls):
        return ('trekking:weblink_add', )

    @property
    def serializable_category(self):
        if not self.category:
            return None
        return {'label': self.category.label,
                'pictogram': os.path.join(settings.MEDIA_URL, self.category.pictogram.name)}


class WebLinkCategory(models.Model):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128, db_column='nom')
    pictogram = models.FileField(verbose_name=_(u"Pictogram"), upload_to=settings.UPLOAD_DIR,
                                 db_column='picto')

    class Meta:
        db_table = 'o_b_web_category'
        verbose_name = _(u"Web link category")
        verbose_name_plural = _(u"Web link categories")
        ordering = ['label']

    def __unicode__(self):
        return u"%s" % self.label

    def pictogram_img(self):
        return u'<img src="%s" />' % (self.pictogram.url if self.pictogram else "")
    pictogram_img.short_description = _("Pictogram")
    pictogram_img.allow_tags = True


class Theme(models.Model):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128, db_column='theme')
    pictogram = models.FileField(verbose_name=_(u"Pictogram"), upload_to=settings.UPLOAD_DIR,
                                 db_column='picto')

    class Meta:
        db_table = 'o_b_theme'
        verbose_name = _(u"Theme")
        verbose_name_plural = _(u"Theme")
        ordering = ['label']

    def __unicode__(self):
        return self.label

    def pictogram_img(self):
        return u'<img src="%s" />' % (self.pictogram.url if self.pictogram else "")
    pictogram_img.short_description = _("Pictogram")
    pictogram_img.allow_tags = True

    @property
    def pictogram_off(self):
        """
        Since pictogram can be a sprite, we want to return the left part of
        the picture (crop right 50%).
        If the pictogram is a square, do not crop.
        """
        pictogram, ext = os.path.splitext(self.pictogram.name)
        pictopath = os.path.join(settings.MEDIA_ROOT, self.pictogram.name)
        output = os.path.join(settings.MEDIA_ROOT, pictogram + '_off' + ext)

        # Recreate only if necessary !
        is_empty = os.path.getsize(output) == 0
        is_newer = os.path.getmtime(pictopath) > os.path.getmtime(output)
        if not os.path.exists(output) or is_empty or is_newer:
            image = Image.open(pictopath)
            w, h = image.size
            if w > h:
                image = image.crop((0, 0, w / 2, h))
            image.save(output)
        return open(output)


class POIManager(models.GeoManager):
    def get_query_set(self):
        return super(POIManager, self).get_query_set().select_related('type')


class POI(PicturesMixin, MapEntityMixin, Topology):

    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    name = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='nom',
                            help_text=_(u"Official name"))
    description = models.TextField(verbose_name=_(u"Description"), db_column='description',
                                   help_text=_(u"History, details,  ..."))
    type = models.ForeignKey('POIType', related_name='pois', verbose_name=_(u"Type"), db_column='type')

    class Meta:
        db_table = 'o_t_poi'
        verbose_name = _(u"POI")
        verbose_name_plural = _(u"POI")

    # Override default manager
    objects = Topology.get_manager_cls(POIManager)()

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.type)

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

    @classmethod
    def path_pois(cls, path):
        return cls.objects.filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_pois(cls, topology):
        return cls.objects.filter(aggregations__path__in=topology.paths.all()).distinct('pk')

Path.add_property('pois', lambda self: POI.path_pois(self))
Topology.add_property('pois', lambda self: Trek.topology_pois(self))
Intervention.add_property('pois', lambda self: self.topology.pois if self.topology else [])
Project.add_property('pois', lambda self: self.edges_by_attr('pois'))


class POIType(models.Model):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128, db_column='nom')
    pictogram = models.FileField(verbose_name=_(u"Pictogram"), upload_to=settings.UPLOAD_DIR,
                                 db_column='picto')

    class Meta:
        db_table = 'o_b_poi'
        verbose_name = _(u"POI")
        verbose_name_plural = _(u"POI")
        ordering = ['label']

    def __unicode__(self):
        return self.label

    @property
    def serializable_pictogram(self):
        return os.path.join(settings.MEDIA_URL, self.pictogram.name)

    def pictogram_img(self):
        return u'<img src="%s" />' % (self.pictogram.url if self.pictogram else "")
    pictogram_img.short_description = _("Pictogram")
    pictogram_img.allow_tags = True
