import os
import logging
import shutil
import datetime
import re

from django.conf import settings
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from easy_thumbnails.alias import aliases
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer
import simplekml
from PIL import Image
from mapentity.models import MapEntityMixin
from mapentity.serializers import plain_text, smart_plain_text

from geotrek.core.models import Path, Topology
from geotrek.common.utils import classproperty
from geotrek.maintenance.models import Intervention, Project

from .templatetags import trekking_tags


logger = logging.getLogger(__name__)


class PicturesMixin(object):
    """A common class to share code between Trek and POI regarding
    attached pictures"""

    @property
    def pictures(self):
        """
        Find first image among attachments.
        Since we allow screenshot to be overriden by attachments
        named 'mapimage', filter it from object pictures.
        """
        if hasattr(self, '_pictures'):
            return self._pictures
        return [a for a in self.attachments.all() if a.is_image
                and a.title != 'mapimage']

    @pictures.setter
    def pictures(self, values):
        self._pictures = values

    @property
    def serializable_pictures(self):
        serialized = []
        for picture in self.pictures:
            thumbnailer = get_thumbnailer(picture.attachment_file)
            try:
                thdetail = thumbnailer.get_thumbnail(aliases.get('medium'))
                thurl = os.path.join(settings.MEDIA_URL, thdetail.name)
            except InvalidImageFormatError:
                thurl = None
                logger.error(_("Image %s invalid or missing from disk.") % picture.attachment_file)
                pass
            serialized.append({
                'author': picture.author,
                'title': picture.title,
                'legend': picture.legend,
                'url': thurl
            })
        return serialized

    @property
    def picture_print(self):
        for picture in self.pictures:
            thumbnailer = get_thumbnailer(picture.attachment_file)
            try:
                return thumbnailer.get_thumbnail(aliases.get('print'))
            except InvalidImageFormatError:
                logger.error(_("Image %s invalid or missing from disk.") % picture.attachment_file)
                pass
        return None

    @property
    def thumbnail(self):
        for picture in self.pictures:
            thumbnailer = get_thumbnailer(picture.attachment_file)
            try:
                return thumbnailer.get_thumbnail(aliases.get('small-square'))
            except InvalidImageFormatError:
                logger.error(_("Image %s invalid or missing from disk.") % picture.attachment_file)
                pass
        return None

    @classproperty
    def thumbnail_verbose_name(cls):
        return _("Thumbnail")

    @property
    def thumbnail_display(self):
        thumbnail = self.thumbnail
        if thumbnail is None:
            return _("None")
        return '<img height="20" width="20" src="%s"/>' % os.path.join(settings.MEDIA_URL, thumbnail.name)

    @property
    def thumbnail_csv_display(self):
        return '' if self.thumbnail is None else os.path.join(settings.MEDIA_URL, self.thumbnail.name)

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
    published = models.BooleanField(verbose_name=_(u"Published"), default=False,
                                    help_text=_(u"Online"), db_column='public')
    publication_date = models.DateField(verbose_name=_(u"Publication date"),
                                        null=True, blank=True, editable=False,
                                        db_column='date_publication')

    description_teaser = models.TextField(verbose_name=_(u"Description teaser"), blank=True,
                                          help_text=_(u"A brief summary (map pop-ups)"), db_column='chapeau')
    description = models.TextField(verbose_name=_(u"Description"), blank=True, db_column='description',
                                   help_text=_(u"Complete description"))
    ambiance = models.TextField(verbose_name=_(u"Ambiance"), blank=True, db_column='ambiance',
                                help_text=_(u"Main attraction and interest"))
    access = models.TextField(verbose_name=_(u"Access"), blank=True, db_column='acces',
                              help_text=_(u"Best way to go"))
    disabled_infrastructure = models.TextField(verbose_name=_(u"Disabled infrastructure"), db_column='handicap',
                                               blank=True, help_text=_(u"Any specific infrastructure"))
    duration = models.FloatField(verbose_name=_(u"Duration"), default=0, blank=True, db_column='duree',
                                 help_text=_(u"In hours"))
    is_park_centered = models.BooleanField(verbose_name=_(u"Is in the midst of the park"), db_column='coeur',
                                           help_text=_(u"Crosses center of park"))
    advised_parking = models.CharField(verbose_name=_(u"Advised parking"), max_length=128, blank=True, db_column='parking',
                                       help_text=_(u"Where to park"))
    parking_location = models.PointField(verbose_name=_(u"Parking location"), db_column='geom_parking',
                                         srid=settings.SRID, spatial_index=False, blank=True, null=True)
    public_transport = models.TextField(verbose_name=_(u"Public transport"), blank=True, db_column='transport',
                                        help_text=_(u"Train, bus (see web links)"))
    advice = models.TextField(verbose_name=_(u"Advice"), blank=True, db_column='recommandation',
                              help_text=_(u"Risks, danger, best period, ..."))
    themes = models.ManyToManyField('Theme', related_name="treks",
                                    db_table="o_r_itineraire_theme", blank=True, null=True, verbose_name=_(u"Themes"),
                                    help_text=_(u"Main theme(s)"))
    networks = models.ManyToManyField('TrekNetwork', related_name="treks",
                                      db_table="o_r_itineraire_reseau", blank=True, null=True, verbose_name=_(u"Networks"),
                                      help_text=_(u"Hiking networks"))
    usages = models.ManyToManyField('Usage', related_name="treks",
                                    db_table="o_r_itineraire_usage", blank=True, null=True, verbose_name=_(u"Usages"),
                                    help_text=_(u"Practicability"))
    route = models.ForeignKey('Route', related_name='treks',
                              blank=True, null=True, verbose_name=_(u"Route"), db_column='parcours')
    difficulty = models.ForeignKey('DifficultyLevel', related_name='treks',
                                   blank=True, null=True, verbose_name=_(u"Difficulty"), db_column='difficulte')
    web_links = models.ManyToManyField('WebLink', related_name="treks",
                                       db_table="o_r_itineraire_web", blank=True, null=True, verbose_name=_(u"Web links"),
                                       help_text=_(u"External resources"))
    related_treks = models.ManyToManyField('self', through='TrekRelationship',
                                           verbose_name=_(u"Related treks"), symmetrical=False,
                                           help_text=_(u"Connections between treks"),
                                           related_name='related_treks+')  # Hide reverse attribute
    information_desks = models.ManyToManyField('InformationDesk',
                                               db_table="o_r_itineraire_renseignement", blank=True, null=True,
                                               verbose_name=_(u"Information desks"),
                                               help_text=_(u"Where to obtain information"))

    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'o_t_itineraire'
        verbose_name = _(u"Trek")
        verbose_name_plural = _(u"Treks")
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.publication_date is None and self.any_published:
            self.publication_date = datetime.date.today()
        if self.publication_date is not None and not self.any_published:
            self.publication_date = None
        super(Trek, self).save(*args, **kwargs)

    @property
    def slug(self):
        return slugify(self.name)

    @models.permalink
    def get_document_public_url(self):
        return ('trekking:trek_document_public', [str(self.pk)])

    @property
    @models.permalink
    def elevation_area_url(self):
        return ('trekking:trek_elevation_area', [str(self.pk)])

    @property
    def any_published(self):
        """Returns True if the trek is published in at least one of the language
        """
        if not settings.TREK_PUBLISHED_BY_LANG:
            return self.published

        for l in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']:
            if getattr(self, 'published_%s' % l[0], False):
                return True
        return False

    @property
    def published_status(self):
        status = []
        for l in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']:
            if settings.TREK_PUBLISHED_BY_LANG:
                published = getattr(self, 'published_%s' % l[0], None) or False
            else:
                published = self.published
            status.append({
                'lang': l[0],
                'language': l[1],
                'status': published
            })
        return status

    @property
    def related(self):
        return self.related_treks.exclude(deleted=True).exclude(pk=self.pk).distinct()

    @property
    def relationships(self):
        # Does not matter if a or b
        return TrekRelationship.objects.filter(trek_a=self)

    @property
    def poi_types(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            # Can't use values_list and must add 'ordering' because of bug:
            # https://code.djangoproject.com/ticket/14930
            values = self.pois.values('ordering', 'type')
        else:
            values = self.pois.values('type')
        pks = [value['type'] for value in values]
        return POIType.objects.filter(pk__in=set(pks))

    def prepare_map_image(self, rooturl):
        """
        We override the default behaviour of map image preparation :
        if the trek has a attached picture file with *title* ``mapimage``, we use it
        as a screenshot.
        TODO: remove this when screenshots are bullet-proof ?
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

    def get_geom_aspect_ratio(self):
        """ Force trek aspect ratio to fit height and width of
        image in public document.
        """
        s = self.get_map_image_size()
        return float(s[0]) / s[1]

    def get_map_image_size(self):
        """
        Map image size in public trek document
        """
        return (13, 11)

    def get_attachment_print(self):
        """
        Look in attachment if there is document to be used as print version
        """
        overriden = self.attachments.filter(title="docprint").get()
        # Must have OpenOffice document mimetype
        if overriden.mimetype != ['application', 'vnd.oasis.opendocument.text']:
            raise overriden.DoesNotExist()
        return os.path.join(settings.MEDIA_ROOT, overriden.attachment_file.name)

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
                 'pictogram': network.serializable_pictogram,
                 'name': network.network} for network in self.networks.all()]

    @property
    def serializable_difficulty(self):
        if not self.difficulty:
            return None
        return {'id': self.difficulty.pk,
                'pictogram': self.difficulty.serializable_pictogram,
                'label': self.difficulty.difficulty}

    @property
    def serializable_themes(self):
        return [{'id': t.pk,
                 'pictogram': t.serializable_pictogram,
                 'label': t.label} for t in self.themes.all()]

    @property
    def serializable_usages(self):
        return [{'id': u.pk,
                 'pictogram': u.serializable_pictogram,
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
                'pictogram': self.route.serializable_pictogram,
                'label': self.route.route}

    @property
    def serializable_web_links(self):
        return [{'id': w.pk,
                 'name': w.name,
                 'category': w.serializable_category,
                 'url': w.url} for w in self.web_links.all()]

    @property
    def information_desk(self):
        """Retrocompatibily method for Geotrek-rando.
        """
        try:
            return self.information_desks.first()
        except (ValueError, InformationDesk.DoesNotExist):
            return None

    @property
    def serializable_information_desk(self):
        return self.information_desk.__json__() if self.information_desk else None

    @property
    def serializable_information_desks(self):
        return [d.__json__() for d in self.information_desks.all()]

    @property
    def serializable_parking_location(self):
        if not self.parking_location:
            return None
        return self.parking_location.transform(settings.API_SRID, clone=True).coords

    @property
    def name_display(self):
        s = u'<a data-pk="%s" href="%s" title="%s">%s</a>' % (self.pk,
                                                              self.get_detail_url(),
                                                              self.name,
                                                              self.name)
        if self.published:
            s = u'<span class="badge badge-success" title="%s">&#x2606;</span> ' % _("Published") + s
        return s

    @property
    def name_csv_display(self):
        return unicode(self.name)

    @property
    def length_kilometer(self):
        return "%.1f" % (self.length / 1000.0)

    @property
    def networks_display(self):
        return ', '.join([unicode(n) for n in self.networks.all()])

    @property
    def districts_display(self):
        return ', '.join([unicode(d) for d in self.districts])

    @property
    def themes_display(self):
        return ', '.join([unicode(n) for n in self.themes.all()])

    @property
    def usages_display(self):
        return ', '.join([unicode(n) for n in self.usages.all()])

    @property
    def city_departure(self):
        cities = self.cities
        return unicode(cities[0]) if len(cities) > 0 else ''

    def kml(self):
        """ Exports trek into KML format, add geometry as linestring and POI
        as place marks """
        kml = simplekml.Kml()
        # Main itinerary
        geom3d = self.geom_3d.transform(4326, clone=True)  # KML uses WGS84
        line = kml.newlinestring(name=self.name,
                                 description=plain_text(self.description),
                                 coords=geom3d.coords)
        line.style.linestyle.color = simplekml.Color.red  # Red
        line.style.linestyle.width = 4  # pixels
        # Place marks
        for poi in self.pois:
            place = poi.geom_3d.transform(settings.API_SRID, clone=True)
            kml.newpoint(name=poi.name,
                         description=plain_text(poi.description),
                         coords=[place.coords])
        return kml._genkml()

    def is_complete(self):
        """It should also have a description, etc.
        """
        mandatory = settings.TREK_COMPLETENESS_FIELDS
        for f in mandatory:
            if not getattr(self, f):
                return False
        return True

    def has_geom_valid(self):
        """A trek should be a LineString, even if it's a loop.
        """
        return (self.geom is not None and self.geom.geom_type.lower() == 'linestring')

    def is_publishable(self):
        return self.is_complete() and self.has_geom_valid()

    @property
    def duration_pretty(self):
        return trekking_tags.duration(self.duration)

    @classmethod
    def path_treks(cls, path):
        treks = cls.objects.existing().filter(aggregations__path=path)
        # The following part prevents conflict with default trek ordering
        # ProgrammingError: SELECT DISTINCT ON expressions must match initial ORDER BY expressions
        return treks.order_by('topo_object').distinct('topo_object')

    @classmethod
    def topology_treks(cls, topology):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            qs = cls.overlapping(topology)
        else:
            area = topology.geom.buffer(settings.TREK_POI_INTERSECTION_MARGIN)
            qs = cls.objects.filter(geom__intersects=area)
        return qs

Path.add_property('treks', Trek.path_treks)
Topology.add_property('treks', Trek.topology_treks)
Intervention.add_property('treks', lambda self: self.topology.treks if self.topology else [])
Project.add_property('treks', lambda self: self.edges_by_attr('treks'))


class TrekRelationshipManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        # Select treks foreign keys by default
        qs = super(TrekRelationshipManager, self).get_queryset().select_related('trek_a', 'trek_b')
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


class PictogramMixin(models.Model):
    pictogram = models.FileField(verbose_name=_(u"Pictogram"), upload_to=settings.UPLOAD_DIR,
                                 db_column='picto', max_length=512, null=True)

    class Meta:
        abstract = True

    @property
    def serializable_pictogram(self):
        return self.pictogram.url if self.pictogram else None

    def pictogram_img(self):
        return u'<img src="%s" />' % (self.pictogram.url if self.pictogram else "")
    pictogram_img.short_description = _("Pictogram")
    pictogram_img.allow_tags = True


class TrekNetwork(PictogramMixin):

    network = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='reseau')

    class Meta:
        db_table = 'o_b_reseau'
        verbose_name = _(u"Trek network")
        verbose_name_plural = _(u"Trek networks")
        ordering = ['network']

    def __unicode__(self):
        return self.network


class Usage(PictogramMixin):

    usage = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='usage')

    class Meta:
        db_table = 'o_b_usage'
        ordering = ['usage']

    def __unicode__(self):
        return self.usage



class Route(PictogramMixin):

    route = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='parcours')

    class Meta:
        db_table = 'o_b_parcours'
        verbose_name = _(u"Route")
        verbose_name_plural = _(u"Routes")
        ordering = ['route']

    def __unicode__(self):
        return self.route


class DifficultyLevel(PictogramMixin):

    """We use an IntegerField for id, since we want to edit it in Admin.
    This column is used to order difficulty levels, especially in public website
    where treks are filtered by difficulty ids.
    """
    id = models.IntegerField(primary_key=True)
    difficulty = models.CharField(verbose_name=_(u"Difficulty level"),
                                  max_length=128, db_column='difficulte')

    class Meta:
        db_table = 'o_b_difficulte'
        verbose_name = _(u"Difficulty level")
        verbose_name_plural = _(u"Difficulty levels")
        ordering = ['id']

    def __unicode__(self):
        return self.difficulty

    def save(self, *args, **kwargs):
        """Manually auto-increment ids"""
        if not self.id:
            try:
                last = self.__class__.objects.all().order_by('-id')[0]
                self.id = last.id + 1
            except IndexError:
                self.id = 1
        super(DifficultyLevel, self).save(*args, **kwargs)


class WebLinkManager(models.Manager):
    def get_queryset(self):
        return super(WebLinkManager, self).get_queryset().select_related('category')


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
        ordering = ['name']

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
                'pictogram': self.category.serializable_pictogram}


class WebLinkCategory(PictogramMixin):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128, db_column='nom')

    class Meta:
        db_table = 'o_b_web_category'
        verbose_name = _(u"Web link category")
        verbose_name_plural = _(u"Web link categories")
        ordering = ['label']

    def __unicode__(self):
        return u"%s" % self.label


class Theme(PictogramMixin):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128, db_column='theme')

    class Meta:
        db_table = 'o_b_theme'
        verbose_name = _(u"Theme")
        verbose_name_plural = _(u"Theme")
        ordering = ['label']

    def __unicode__(self):
        return self.label

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


class InformationDesk(models.Model):

    name = models.CharField(verbose_name=_(u"Title"), max_length=256, db_column='nom')
    description = models.TextField(verbose_name=_(u"Description"), blank=True, db_column='description',
                                   help_text=_(u"Brief description"))
    phone = models.CharField(verbose_name=_(u"Phone"), max_length=32,
                             blank=True, null=True, db_column='telephone')
    email = models.EmailField(verbose_name=_(u"Email"), max_length=256, db_column='email',
                              blank=True, null=True)
    website = models.URLField(verbose_name=_(u"Website"), max_length=256, db_column='website',
                              blank=True, null=True)
    photo = models.FileField(verbose_name=_(u"Photo"), upload_to=settings.UPLOAD_DIR,
                             db_column='photo', max_length=512, blank=True, null=True)

    street = models.CharField(verbose_name=_(u"Street"), max_length=256,
                              blank=True, null=True, db_column='rue')
    postal_code = models.IntegerField(verbose_name=_(u"Postal code"),
                                      blank=True, null=True, db_column='code')
    municipality = models.CharField(verbose_name=_(u"Municipality"),
                                    blank=True, null=True,
                                    max_length=256, db_column='commune')

    geom = models.PointField(verbose_name=_(u"Emplacement"), db_column='geom',
                             blank=True, null=True,
                             srid=settings.SRID, spatial_index=False)

    class Meta:
        db_table = 'o_b_renseignement'
        verbose_name = _(u"Information desk")
        verbose_name_plural = _(u"Information desks")
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def __json__(self):
        return {
            'name': self.name,
            'description': self.description,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'photo_url': self.photo_url,
            'street': self.street,
            'postal_code': self.postal_code,
            'municipality': self.municipality,
            'latitude': self.latitude,
            'longitude': self.longitude,
        }

    @property
    def description_strip(self):
        nobr = re.compile(r'(\s*<br.*?>)+\s*', re.I)
        newlines = nobr.sub("\n", self.description)
        print newlines
        return smart_plain_text(newlines)

    @property
    def latitude(self):
        if self.geom:
            api_geom = self.geom.transform(settings.API_SRID, clone=True)
            return api_geom.y
        return None

    @property
    def longitude(self):
        if self.geom:
            api_geom = self.geom.transform(settings.API_SRID, clone=True)
            return api_geom.x
        return None

    @property
    def photo_url(self):
        if not self.photo:
            return None
        thumbnailer = get_thumbnailer(self.photo)
        try:
            thumb_detail = thumbnailer.get_thumbnail(aliases.get('thumbnail'))
            thumb_url = os.path.join(settings.MEDIA_URL, thumb_detail.name)
        except InvalidImageFormatError:
            thumb_url = None
            logger.error(_("Image %s invalid or missing from disk.") % self.photo)
        return thumb_url


class POIManager(models.GeoManager):
    def get_queryset(self):
        return super(POIManager, self).get_queryset().select_related('type')


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
        return u'<a data-pk="%s" href="%s" title="%s">%s</a>' % (self.pk,
                                                                 self.get_detail_url(),
                                                                 self.name,
                                                                 self.name)

    @property
    def name_csv_display(self):
        return unicode(self.name)

    @property
    def serializable_type(self):
        return {'label': self.type.label,
                'pictogram': self.type.serializable_pictogram}

    @classmethod
    def path_pois(cls, path):
        return cls.objects.filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_pois(cls, topology):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            qs = cls.overlapping(topology)
        else:
            area = topology.geom.buffer(settings.TREK_POI_INTERSECTION_MARGIN)
            qs = cls.objects.filter(geom__intersects=area)
        return qs

Path.add_property('pois', POI.path_pois)
Topology.add_property('pois', POI.topology_pois)
Intervention.add_property('pois', lambda self: self.topology.pois if self.topology else [])
Project.add_property('pois', lambda self: self.edges_by_attr('pois'))


class POIType(PictogramMixin):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128, db_column='nom')

    class Meta:
        db_table = 'o_b_poi'
        verbose_name = _(u"POI type")
        verbose_name_plural = _(u"POI types")
        ordering = ['label']

    def __unicode__(self):
        return self.label
