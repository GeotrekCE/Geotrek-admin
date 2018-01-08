import os
import re
import logging

from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import get_language, ugettext_lazy as _
from django.utils.formats import date_format

from easy_thumbnails.alias import aliases
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer
from mapentity import registry
from mapentity.models import MapEntityMixin
from mapentity.serializers import plain_text, smart_plain_text
from modeltranslation.manager import MultilingualManager

from geotrek.authent.models import StructureRelated
from geotrek.core.models import Topology
from geotrek.common.mixins import (NoDeleteMixin, TimeStampedModelMixin,
                                   PictogramMixin, OptionalPictogramMixin,
                                   PublishableMixin, PicturesMixin,
                                   AddPropertyMixin)
from geotrek.common.models import Theme
from geotrek.common.utils import intersecting

from extended_choices import Choices


logger = logging.getLogger(__name__)

DATA_SOURCE_TYPES = Choices(
    ('GEOJSON', 'GEOJSON', _("GeoJSON")),
    ('TOURINFRANCE', 'TOURINFRANCE', _("TourInFrance")),
    ('SITRA', 'SITRA', _("Sitra")),
)


def _get_target_choices():
    """ Populate choices using installed apps names.
    """
    apps = [('public', _("Public website"))]
    for model, entity in registry.registry.items():
        if entity.menu:
            appname = model._meta.app_label.lower()
            apps.append((appname, unicode(entity.label)))
    return tuple(apps)


class InformationDeskType(PictogramMixin):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128, db_column='label')

    class Meta:
        db_table = 't_b_type_renseignement'
        verbose_name = _(u"Information desk type")
        verbose_name_plural = _(u"Information desk types")
        ordering = ['label']

    def __unicode__(self):
        return self.label


class InformationDesk(models.Model):

    name = models.CharField(verbose_name=_(u"Title"), max_length=256, db_column='nom')
    type = models.ForeignKey(InformationDeskType, verbose_name=_(u"Type"),
                             related_name='desks', db_column='type')
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
    postal_code = models.CharField(verbose_name=_(u"Postal code"), max_length=8,
                                   blank=True, null=True, db_column='code')
    municipality = models.CharField(verbose_name=_(u"Municipality"),
                                    blank=True, null=True,
                                    max_length=256, db_column='commune')

    geom = models.PointField(verbose_name=_(u"Emplacement"), db_column='geom',
                             blank=True, null=True,
                             srid=settings.SRID, spatial_index=False)

    objects = models.GeoManager()

    class Meta:
        db_table = 't_b_renseignement'
        verbose_name = _(u"Information desk")
        verbose_name_plural = _(u"Information desks")
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @property
    def description_strip(self):
        """Used in trek public template.
        """
        nobr = re.compile(r'(\s*<br.*?>)+\s*', re.I)
        newlines = nobr.sub("\n", self.description)
        return smart_plain_text(newlines)

    @property
    def serializable_type(self):
        return {
            'id': self.type.id,
            'label': self.type.label,
            'pictogram': self.type.pictogram.url,
        }

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
    def thumbnail(self):
        if not self.photo:
            return None
        thumbnailer = get_thumbnailer(self.photo)
        try:
            return thumbnailer.get_thumbnail(aliases.get('thumbnail'))
        except InvalidImageFormatError:
            logger.warning(_("Image %s invalid or missing from disk.") % self.photo)
            return None

    @property
    def photo_url(self):
        thumbnail = self.thumbnail
        if not thumbnail:
            return None
        return os.path.join(settings.MEDIA_URL, thumbnail.name)


GEOMETRY_TYPES = Choices(
    ('POINT', 'point', _('Point')),
    ('LINE', 'line', _('Line')),
    ('POLYGON', 'polygon', _('Polygon')),
    ('ANY', 'any', _('Any')),
)


class TouristicContentCategory(PictogramMixin):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128, db_column='nom')
    geometry_type = models.CharField(db_column="type_geometrie", max_length=16,
                                     choices=GEOMETRY_TYPES, default=GEOMETRY_TYPES.POINT)
    type1_label = models.CharField(verbose_name=_(u"First list label"), max_length=128,
                                   db_column='label_type1', blank=True)
    type2_label = models.CharField(verbose_name=_(u"Second list label"), max_length=128,
                                   db_column='label_type2', blank=True)
    order = models.IntegerField(verbose_name=_(u"Order"), null=True, blank=True, db_column='tri',
                                help_text=_(u"Alphabetical order if blank"))

    id_prefix = 'C'

    class Meta:
        db_table = 't_b_contenu_touristique_categorie'
        verbose_name = _(u"Touristic content category")
        verbose_name_plural = _(u"Touristic content categories")
        ordering = ['order', 'label']

    def __unicode__(self):
        return self.label

    @property
    def prefixed_id(self):
        return '{prefix}{id}'.format(prefix=self.id_prefix, id=self.id)


class TouristicContentType(OptionalPictogramMixin):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128, db_column='nom')
    category = models.ForeignKey(TouristicContentCategory, related_name='types',
                                 verbose_name=_(u"Category"), db_column='categorie')
    # Choose in which list of choices this type will appear
    in_list = models.IntegerField(choices=((1, _(u"First")), (2, _(u"Second"))), db_column='liste_choix')

    class Meta:
        db_table = 't_b_contenu_touristique_type'
        verbose_name = _(u"Touristic content type")
        verbose_name_plural = _(u"Touristic content type")
        ordering = ['label']

    def __unicode__(self):
        return self.label


class TouristicContentType1Manager(MultilingualManager):
    def get_queryset(self):
        return super(TouristicContentType1Manager, self).get_queryset().filter(in_list=1)


class TouristicContentType2Manager(MultilingualManager):
    def get_queryset(self):
        return super(TouristicContentType2Manager, self).get_queryset().filter(in_list=2)


class TouristicContentType1(TouristicContentType):
    objects = TouristicContentType1Manager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('in_list').default = 1
        super(TouristicContentType1, self).__init__(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = _(u"Type")
        verbose_name_plural = _(u"First list types")


class TouristicContentType2(TouristicContentType):
    objects = TouristicContentType2Manager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('in_list').default = 2
        super(TouristicContentType2, self).__init__(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = _(u"Type")
        verbose_name_plural = _(u"Second list types")


class ReservationSystem(models.Model):
    name = models.CharField(verbose_name=_(u"Name"), max_length=256,
                            blank=False, null=False, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 't_b_systeme_reservation'
        verbose_name = _(u"Reservation system")
        verbose_name_plural = _(u"Reservation systems")


class TouristicContent(AddPropertyMixin, PublishableMixin, MapEntityMixin, StructureRelated,
                       TimeStampedModelMixin, PicturesMixin, NoDeleteMixin):
    """ A generic touristic content (accomodation, museum, etc.) in the park
    """
    description_teaser = models.TextField(verbose_name=_(u"Description teaser"), blank=True,
                                          help_text=_(u"A brief summary"), db_column='chapeau')
    description = models.TextField(verbose_name=_(u"Description"), blank=True, db_column='description',
                                   help_text=_(u"Complete description"))
    themes = models.ManyToManyField(Theme, related_name="touristiccontents",
                                    db_table="t_r_contenu_touristique_theme", blank=True, verbose_name=_(u"Themes"),
                                    help_text=_(u"Main theme(s)"))
    geom = models.GeometryField(verbose_name=_(u"Location"), srid=settings.SRID)
    category = models.ForeignKey(TouristicContentCategory, related_name='contents',
                                 verbose_name=_(u"Category"), db_column='categorie')
    contact = models.TextField(verbose_name=_(u"Contact"), blank=True, db_column='contact',
                               help_text=_(u"Address, phone, etc."))
    email = models.EmailField(verbose_name=_(u"Email"), max_length=256, db_column='email',
                              blank=True, null=True)
    website = models.URLField(verbose_name=_(u"Website"), max_length=256, db_column='website',
                              blank=True, null=True)
    practical_info = models.TextField(verbose_name=_(u"Practical info"), blank=True, db_column='infos_pratiques',
                                      help_text=_(u"Anything worth to know"))
    type1 = models.ManyToManyField(TouristicContentType, related_name='contents1',
                                   verbose_name=_(u"Type 1"), db_table="t_r_contenu_touristique_type1",
                                   blank=True)
    type2 = models.ManyToManyField(TouristicContentType, related_name='contents2',
                                   verbose_name=_(u"Type 2"), db_table="t_r_contenu_touristique_type2",
                                   blank=True)
    source = models.ManyToManyField('common.RecordSource',
                                    blank=True, related_name='touristiccontents',
                                    verbose_name=_("Source"), db_table='t_r_contenu_touristique_source')
    portal = models.ManyToManyField('common.TargetPortal',
                                    blank=True, related_name='touristiccontents',
                                    verbose_name=_("Portal"), db_table='t_r_contenu_touristique_portal')
    eid = models.CharField(verbose_name=_(u"External id"), max_length=128, blank=True, null=True, db_column='id_externe')
    reservation_system = models.ForeignKey(ReservationSystem, verbose_name=_(u"Reservation system"),
                                           blank=True, null=True)
    reservation_id = models.CharField(verbose_name=_(u"Reservation ID"), max_length=128,
                                      blank=True, db_column='id_reservation')
    approved = models.BooleanField(verbose_name=_(u"Approved"), default=False, db_column='labellise')

    objects = NoDeleteMixin.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 't_t_contenu_touristique'
        verbose_name = _(u"Touristic content")
        verbose_name_plural = _(u"Touristic contents")

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_document_public_url(self):
        """ Override ``geotrek.common.mixins.PublishableMixin``
        """
        return ('tourism:touristiccontent_document_public', [], {'lang': get_language(), 'pk': self.pk, 'slug': self.slug})

    @property
    def districts_display(self):
        return ', '.join([unicode(d) for d in self.districts])

    @property
    def type1_label(self):
        return self.category.type1_label

    @property
    def type2_label(self):
        return self.category.type2_label

    @property
    def type1_display(self):
        return ', '.join([unicode(n) for n in self.type1.all()])

    @property
    def type2_display(self):
        return ', '.join([unicode(n) for n in self.type2.all()])

    @property
    def prefixed_category_id(self):
        return self.category.prefixed_id

    def distance(self, to_cls):
        return settings.TOURISM_INTERSECTION_MARGIN

    @property
    def type(self):
        """Fake type to simulate POI for mobile app v1"""
        return self.category

    @property
    def min_elevation(self):
        return 0

    @property
    def max_elevation(self):
        return 0

    @property
    def portal_display(self):
        return ', '.join([unicode(portal) for portal in self.portal.all()])

    @property
    def source_display(self):
        return ','.join([unicode(source) for source in self.source.all()])

    @property
    def themes_display(self):
        return ','.join([unicode(source) for source in self.themes.all()])

    @property
    def extent(self):
        return self.geom.buffer(10).transform(settings.API_SRID, clone=True).extent

    @property
    def rando_url(self):
        category_slug = _(u'touristic-content')
        return '{}/{}/'.format(category_slug, self.slug)

    @property
    def meta_description(self):
        return plain_text(self.description_teaser or self.description)[:500]


Topology.add_property('touristic_contents', lambda self: intersecting(TouristicContent, self), _(u"Touristic contents"))
Topology.add_property('published_touristic_contents', lambda self: intersecting(TouristicContent, self).filter(published=True), _(u"Published touristic contents"))
TouristicContent.add_property('touristic_contents', lambda self: intersecting(TouristicContent, self), _(u"Touristic contents"))
TouristicContent.add_property('published_touristic_contents', lambda self: intersecting(TouristicContent, self).filter(published=True), _(u"Published touristic contents"))


class TouristicEventType(OptionalPictogramMixin):

    type = models.CharField(verbose_name=_(u"Type"), max_length=128, db_column='type')

    class Meta:
        db_table = 't_b_evenement_touristique_type'
        verbose_name = _(u"Touristic event type")
        verbose_name_plural = _(u"Touristic event types")
        ordering = ['type']

    def __unicode__(self):
        return self.type


class TouristicEvent(AddPropertyMixin, PublishableMixin, MapEntityMixin, StructureRelated,
                     PicturesMixin, TimeStampedModelMixin, NoDeleteMixin):
    """ A touristic event (conference, workshop, etc.) in the park
    """
    description_teaser = models.TextField(verbose_name=_(u"Description teaser"), blank=True,
                                          help_text=_(u"A brief summary"), db_column='chapeau')
    description = models.TextField(verbose_name=_(u"Description"), blank=True, db_column='description',
                                   help_text=_(u"Complete description"))
    themes = models.ManyToManyField(Theme, related_name="touristic_events",
                                    db_table="t_r_evenement_touristique_theme", blank=True, verbose_name=_(u"Themes"),
                                    help_text=_(u"Main theme(s)"))
    geom = models.PointField(verbose_name=_(u"Location"), srid=settings.SRID)
    begin_date = models.DateField(blank=True, null=True, verbose_name=_(u"Begin date"), db_column='date_debut')
    end_date = models.DateField(blank=True, null=True, verbose_name=_(u"End date"), db_column='date_fin')
    duration = models.CharField(verbose_name=_(u"Duration"), max_length=64, blank=True, db_column='duree',
                                help_text=_(u"3 days, season, ..."))
    meeting_point = models.CharField(verbose_name=_(u"Meeting point"), max_length=256, blank=True, db_column='point_rdv',
                                     help_text=_(u"Where exactly ?"))
    meeting_time = models.TimeField(verbose_name=_(u"Meeting time"), blank=True, null=True, db_column='heure_rdv',
                                    help_text=_(u"11:00, 23:30"))
    contact = models.TextField(verbose_name=_(u"Contact"), blank=True, db_column='contact')
    email = models.EmailField(verbose_name=_(u"Email"), max_length=256, db_column='email',
                              blank=True, null=True)
    website = models.URLField(verbose_name=_(u"Website"), max_length=256, db_column='website',
                              blank=True, null=True)
    organizer = models.CharField(verbose_name=_(u"Organizer"), max_length=256, blank=True, db_column='organisateur')
    speaker = models.CharField(verbose_name=_(u"Speaker"), max_length=256, blank=True, db_column='intervenant')
    type = models.ForeignKey(TouristicEventType, verbose_name=_(u"Type"), blank=True, null=True, db_column='type')
    accessibility = models.CharField(verbose_name=_(u"Accessibility"), max_length=256, blank=True, db_column='accessibilite')
    participant_number = models.CharField(verbose_name=_(u"Number of participants"), max_length=256, blank=True, db_column='nb_places')
    booking = models.TextField(verbose_name=_(u"Booking"), blank=True, db_column='reservation')
    target_audience = models.CharField(verbose_name=_(u"Target audience"), max_length=128, blank=True, null=True, db_column='public_vise')
    practical_info = models.TextField(verbose_name=_(u"Practical info"), blank=True, db_column='infos_pratiques',
                                      help_text=_(u"Recommandations / To plan / Advices"))
    source = models.ManyToManyField('common.RecordSource',
                                    blank=True, related_name='touristicevents',
                                    verbose_name=_("Source"), db_table='t_r_evenement_touristique_source')
    portal = models.ManyToManyField('common.TargetPortal',
                                    blank=True, related_name='touristicevents',
                                    verbose_name=_("Portal"), db_table='t_r_evenement_touristique_portal')
    eid = models.CharField(verbose_name=_(u"External id"), max_length=128, blank=True, null=True, db_column='id_externe')
    approved = models.BooleanField(verbose_name=_(u"Approved"), default=False, db_column='labellise')

    objects = NoDeleteMixin.get_manager_cls(models.GeoManager)()

    category_id_prefix = 'E'

    class Meta:
        db_table = 't_t_evenement_touristique'
        verbose_name = _(u"Touristic event")
        verbose_name_plural = _(u"Touristic events")
        ordering = ['-begin_date']

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_document_public_url(self):
        """ Override ``geotrek.common.mixins.PublishableMixin``
        """
        return ('tourism:touristicevent_document_public', [], {'lang': get_language(), 'pk': self.pk, 'slug': self.slug})

    @property
    def type1(self):
        return [self.type] if self.type else []

    @property
    def type2(self):
        return []

    @property
    def districts_display(self):
        return ', '.join([unicode(d) for d in self.districts])

    @property
    def dates_display(self):
        if not self.begin_date and not self.end_date:
            return u""
        elif not self.end_date:
            return _(u"starting from {begin}").format(
                begin=date_format(self.begin_date, 'SHORT_DATE_FORMAT'))
        elif not self.begin_date:
            return _(u"up to {end}").format(
                end=date_format(self.end_date, 'SHORT_DATE_FORMAT'))
        elif self.begin_date == self.end_date:
            return date_format(self.begin_date, 'SHORT_DATE_FORMAT')
        else:
            return _(u"from {begin} to {end}").format(
                begin=date_format(self.begin_date, 'SHORT_DATE_FORMAT'),
                end=date_format(self.end_date, 'SHORT_DATE_FORMAT'))

    @property
    def prefixed_category_id(self):
        return self.category_id_prefix

    def distance(self, to_cls):
        return settings.TOURISM_INTERSECTION_MARGIN

    @property
    def portal_display(self):
        return ', '.join([unicode(portal) for portal in self.portal.all()])

    @property
    def source_display(self):
        return ', '.join([unicode(source) for source in self.source.all()])

    @property
    def themes_display(self):
        return ','.join([unicode(source) for source in self.themes.all()])

    @property
    def rando_url(self):
        category_slug = _(u'touristic-event')
        return '{}/{}/'.format(category_slug, self.slug)

    @property
    def meta_description(self):
        return plain_text(self.description_teaser or self.description)[:500]


TouristicEvent.add_property('touristic_contents', lambda self: intersecting(TouristicContent, self), _(u"Touristic contents"))
TouristicEvent.add_property('published_touristic_contents', lambda self: intersecting(TouristicContent, self).filter(published=True), _(u"Published touristic contents"))
Topology.add_property('touristic_events', lambda self: intersecting(TouristicEvent, self), _(u"Touristic events"))
Topology.add_property('published_touristic_events', lambda self: intersecting(TouristicEvent, self).filter(published=True), _(u"Published touristic events"))
TouristicContent.add_property('touristic_events', lambda self: intersecting(TouristicEvent, self), _(u"Touristic events"))
TouristicContent.add_property('published_touristic_events', lambda self: intersecting(TouristicEvent, self).filter(published=True), _(u"Published touristic events"))
TouristicEvent.add_property('touristic_events', lambda self: intersecting(TouristicEvent, self), _(u"Touristic events"))
TouristicEvent.add_property('published_touristic_events', lambda self: intersecting(TouristicEvent, self).filter(published=True), _(u"Published touristic events"))
