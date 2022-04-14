import logging
import os
import uuid
from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.indexes import GistIndex
from django.db.models.query_utils import Q
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _
from easy_thumbnails.alias import aliases
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer
from extended_choices import Choices

from geotrek.authent.models import StructureRelated
from geotrek.common.mixins.models import (AddPropertyMixin, NoDeleteMixin, OptionalPictogramMixin, PictogramMixin,
                                          PicturesMixin, PublishableMixin, TimeStampedModelMixin)
from geotrek.common.models import ReservationSystem, Theme
from geotrek.common.utils import intersecting
from geotrek.core.models import Topology
from geotrek.zoning.mixins import ZoningPropertiesMixin
from mapentity.models import MapEntityMixin
from mapentity.serializers import plain_text

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.manager import MultilingualManager
else:
    from django.db.models import Manager as MultilingualManager

logger = logging.getLogger(__name__)


class InformationDeskType(PictogramMixin):

    label = models.CharField(verbose_name=_("Label"), max_length=128)

    class Meta:
        verbose_name = _("Information desk type")
        verbose_name_plural = _("Information desk types")
        ordering = ['label']

    def __str__(self):
        return self.label


class LabelAccessibility(PictogramMixin):

    label = models.CharField(verbose_name=_("Label"), max_length=128)

    class Meta:
        verbose_name = _("Label accessibility")
        verbose_name_plural = _("Labels accessibility")
        ordering = ['label']

    def __str__(self):
        return self.label


class InformationDesk(models.Model):

    name = models.CharField(verbose_name=_("Title"), max_length=256)
    type = models.ForeignKey(InformationDeskType, verbose_name=_("Type"), on_delete=models.CASCADE,
                             related_name='desks')
    description = models.TextField(verbose_name=_("Description"), blank=True,
                                   help_text=_("Brief description"))
    phone = models.CharField(verbose_name=_("Phone"), max_length=32,
                             blank=True, null=True)
    email = models.EmailField(verbose_name=_("Email"), max_length=256,
                              blank=True, null=True)
    website = models.URLField(verbose_name=_("Website"), max_length=256,
                              blank=True, null=True)
    photo = models.FileField(verbose_name=_("Photo"), upload_to=settings.UPLOAD_DIR,
                             max_length=512, blank=True, null=True)

    street = models.CharField(verbose_name=_("Street"), max_length=256,
                              blank=True, null=True)
    postal_code = models.CharField(verbose_name=_("Postal code"), max_length=8,
                                   blank=True, null=True)
    municipality = models.CharField(verbose_name=_("Municipality"),
                                    blank=True, null=True,
                                    max_length=256)
    accessibility = models.TextField(verbose_name=_("Accessibility"), blank=True)
    label_accessibility = models.ForeignKey(LabelAccessibility, verbose_name=_("Label accessibility"),
                                            on_delete=models.PROTECT, related_name='desks', blank=True, null=True)
    geom = models.PointField(verbose_name=_("Emplacement"),
                             blank=True, null=True,
                             srid=settings.SRID, spatial_index=False)

    objects = models.Manager()

    class Meta:
        verbose_name = _("Information desk")
        verbose_name_plural = _("Information desks")
        ordering = ['name']
        indexes = [
            GistIndex(name='informationdesk_geom_gist_idx', fields=['geom']),
        ]

    def __str__(self):
        return self.name

    @property
    def latitude(self):
        return self.geom.transform(settings.API_SRID, clone=True).y if self.geom else None

    @property
    def longitude(self):
        return self.geom.transform(settings.API_SRID, clone=True).x if self.geom else None

    @property
    def thumbnail(self):
        if not self.photo:
            return None
        thumbnailer = get_thumbnailer(self.photo)
        try:
            return thumbnailer.get_thumbnail(aliases.get('thumbnail'))
        except (IOError, InvalidImageFormatError):
            logger.warning(_("Image %s invalid or missing from disk.") % self.photo)
            return None

    @property
    def resized_picture(self):
        if not self.photo:
            return None
        thumbnailer = get_thumbnailer(self.photo)
        try:
            return thumbnailer.get_thumbnail(aliases.get('medium'))
        except (IOError, InvalidImageFormatError):
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

    label = models.CharField(verbose_name=_("Label"), max_length=128)
    geometry_type = models.CharField(max_length=16, choices=GEOMETRY_TYPES, default=GEOMETRY_TYPES.POINT)
    type1_label = models.CharField(verbose_name=_("First list label"), max_length=128,
                                   blank=True)
    type2_label = models.CharField(verbose_name=_("Second list label"), max_length=128,
                                   blank=True)
    order = models.IntegerField(verbose_name=_("Order"), null=True, blank=True,
                                help_text=_("Alphabetical order if blank"))
    color = ColorField(verbose_name=_("Color"), default='#444444',
                       help_text=_("Color of the category, only used in mobile."))  # To be implemented in Geotrek-rando

    id_prefix = 'C'

    class Meta:
        verbose_name = _("Touristic content category")
        verbose_name_plural = _("Touristic content categories")
        ordering = ['order', 'label']

    def __str__(self):
        return self.label

    @property
    def prefixed_id(self):
        return '{prefix}{id}'.format(prefix=self.id_prefix, id=self.id)


class TouristicContentTypeFilteringManager(MultilingualManager):
    def has_content_published_not_deleted_in_list(self, list_index, category=None, portals=None, language=None):
        """ Retrieves content types for which there exists an event that is published and not deleted in list (type1 or type2)
        """
        i = list_index
        q_total = Q()
        qs = super().get_queryset().filter(in_list=i)
        # Building following logic :
        # return type1 if:
        #            (contents1__portal__in==portals)
        #          & (contents1__category==category)
        #          & (contents1_published_fr | contents1_published_en)
        #          & not(contents1_deleted)
        #
        # q_total  =      q_portal
        #               & q_category
        #               & q_lang
        #               & q_deleted

        q_portal = Q()
        if portals:
            portal_field_name = f"contents{i}__portal__in"
            q_portal = Q(**{portal_field_name: portals})

        q_category = Q()
        if category:
            category_field_name = f"contents{i}__category"
            q_category = Q(**{category_field_name: category})

        if language:
            published_field_name = f"contents{i}__published_{language}"
            q_lang = Q(**{published_field_name: True})
        else:
            q_lang = Q()
            for lang in settings.MODELTRANSLATION_LANGUAGES:
                published_field_name = f"contents{i}__published_{lang}"
                q_lang |= Q(**{published_field_name: True})

        deleted_field_name = f"contents{i}__deleted"
        q_deleted = Q(**{deleted_field_name: False})

        q_total = q_portal & q_category & q_lang & q_deleted

        return qs.filter(q_total).distinct()


class TouristicContentType(OptionalPictogramMixin):
    objects = TouristicContentTypeFilteringManager()
    label = models.CharField(verbose_name=_("Label"), max_length=128)
    category = models.ForeignKey(TouristicContentCategory, related_name='types', on_delete=models.CASCADE,
                                 verbose_name=_("Category"))
    # Choose in which list of choices this type will appear
    in_list = models.IntegerField(choices=((1, _("First")), (2, _("Second"))))

    class Meta:
        verbose_name = _("Touristic content type")
        verbose_name_plural = _("Touristic content type")
        ordering = ['label']

    def __str__(self):
        return self.label


class TouristicContentType1Manager(MultilingualManager):
    def get_queryset(self):
        return super().get_queryset().filter(in_list=1)


class TouristicContentType2Manager(MultilingualManager):
    def get_queryset(self):
        return super().get_queryset().filter(in_list=2)


class TouristicContentType1(TouristicContentType):
    objects = TouristicContentType1Manager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('in_list').default = 1
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = _("Type1")
        verbose_name_plural = _("First list types")


class TouristicContentType2(TouristicContentType):
    objects = TouristicContentType2Manager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('in_list').default = 2
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = _("Type2")
        verbose_name_plural = _("Second list types")


class TouristicContent(ZoningPropertiesMixin, AddPropertyMixin, PublishableMixin, MapEntityMixin, StructureRelated,
                       TimeStampedModelMixin, PicturesMixin, NoDeleteMixin):
    """ A generic touristic content (accomodation, museum, etc.) in the park
    """
    description_teaser = models.TextField(verbose_name=_("Description teaser"), blank=True,
                                          help_text=_("A brief summary"))
    description = models.TextField(verbose_name=_("Description"), blank=True,
                                   help_text=_("Complete description"))
    themes = models.ManyToManyField(Theme, related_name="touristiccontents",
                                    blank=True, verbose_name=_("Themes"),
                                    help_text=_("Main theme(s)"))
    geom = models.GeometryField(verbose_name=_("Location"), srid=settings.SRID)
    category = models.ForeignKey(TouristicContentCategory, related_name='contents', on_delete=models.CASCADE,
                                 verbose_name=_("Category"))
    contact = models.TextField(verbose_name=_("Contact"), blank=True,
                               help_text=_("Address, phone, etc."))
    email = models.EmailField(verbose_name=_("Email"), max_length=256,
                              blank=True, null=True)
    website = models.URLField(verbose_name=_("Website"), max_length=256,
                              blank=True, null=True)
    practical_info = models.TextField(verbose_name=_("Practical info"), blank=True,
                                      help_text=_("Anything worth to know"))
    type1 = models.ManyToManyField(TouristicContentType1, related_name='contents1',
                                   verbose_name=_("Type 1"),
                                   blank=True)
    type2 = models.ManyToManyField(TouristicContentType2, related_name='contents2',
                                   verbose_name=_("Type 2"),
                                   blank=True)
    source = models.ManyToManyField('common.RecordSource',
                                    blank=True, related_name='touristiccontents',
                                    verbose_name=_("Source"))
    portal = models.ManyToManyField('common.TargetPortal',
                                    blank=True, related_name='touristiccontents',
                                    verbose_name=_("Portal"))
    accessibility = models.TextField(verbose_name=_("Accessibility"), blank=True)
    label_accessibility = models.ForeignKey(LabelAccessibility, verbose_name=_("Label accessibility"),
                                            on_delete=models.CASCADE, related_name='contents', blank=True,
                                            null=True)
    eid = models.CharField(verbose_name=_("External id"), max_length=1024, blank=True, null=True)
    reservation_system = models.ForeignKey(ReservationSystem, verbose_name=_("Reservation system"),
                                           on_delete=models.CASCADE, blank=True, null=True)
    reservation_id = models.CharField(verbose_name=_("Reservation ID"), max_length=1024,
                                      blank=True)
    approved = models.BooleanField(verbose_name=_("Approved"), default=False,
                                   help_text=_("Indicates whether the content has a label or brand"))
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        verbose_name = _("Touristic content")
        verbose_name_plural = _("Touristic contents")

    def __str__(self):
        return self.name

    @property
    def districts_display(self):
        return ', '.join([str(d) for d in self.districts])

    @property
    def type1_label(self):
        return self.category.type1_label

    @property
    def type2_label(self):
        return self.category.type2_label

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
    def extent(self):
        return self.geom.buffer(10).transform(settings.API_SRID, clone=True).extent

    @property
    def rando_url(self):
        category_slug = _('touristic-content')
        return '{}/{}/'.format(category_slug, self.slug)

    @property
    def meta_description(self):
        return plain_text(self.description_teaser or self.description)[:500]


Topology.add_property('touristic_contents', lambda self: intersecting(TouristicContent, self).order_by(*settings.TOURISTIC_CONTENTS_API_ORDER), _("Touristic contents"))
Topology.add_property('published_touristic_contents', lambda self: intersecting(TouristicContent, self).filter(published=True).order_by(*settings.TOURISTIC_CONTENTS_API_ORDER), _("Published touristic contents"))
TouristicContent.add_property('touristic_contents', lambda self: intersecting(TouristicContent, self).order_by(*settings.TOURISTIC_CONTENTS_API_ORDER), _("Touristic contents"))
TouristicContent.add_property('published_touristic_contents', lambda self: intersecting(TouristicContent, self).filter(published=True).order_by(*settings.TOURISTIC_CONTENTS_API_ORDER), _("Published touristic contents"))


class TouristicEventType(OptionalPictogramMixin):

    type = models.CharField(verbose_name=_("Type"), max_length=128)

    class Meta:
        verbose_name = _("Touristic event type")
        verbose_name_plural = _("Touristic event types")
        ordering = ['type']

    def __str__(self):
        return self.type


class TouristicEvent(ZoningPropertiesMixin, AddPropertyMixin, PublishableMixin, MapEntityMixin, StructureRelated,
                     PicturesMixin, TimeStampedModelMixin, NoDeleteMixin):
    """ A touristic event (conference, workshop, etc.) in the park
    """
    description_teaser = models.TextField(verbose_name=_("Description teaser"), blank=True,
                                          help_text=_("A brief summary"))
    description = models.TextField(verbose_name=_("Description"), blank=True,
                                   help_text=_("Complete description"))
    themes = models.ManyToManyField(Theme, related_name="touristic_events",
                                    blank=True, verbose_name=_("Themes"),
                                    help_text=_("Main theme(s)"))
    geom = models.PointField(verbose_name=_("Location"), srid=settings.SRID)
    begin_date = models.DateField(blank=True, null=True, verbose_name=_("Begin date"))
    end_date = models.DateField(blank=True, null=True, verbose_name=_("End date"))
    duration = models.CharField(verbose_name=_("Duration"), max_length=64, blank=True,
                                help_text=_("3 days, season, ..."))
    meeting_point = models.CharField(verbose_name=_("Meeting point"), max_length=256, blank=True,
                                     help_text=_("Where exactly ?"))
    meeting_time = models.TimeField(verbose_name=_("Meeting time"), blank=True, null=True,
                                    help_text=_("11:00, 23:30"))
    contact = models.TextField(verbose_name=_("Contact"), blank=True)
    email = models.EmailField(verbose_name=_("Email"), max_length=256,
                              blank=True, null=True)
    website = models.URLField(verbose_name=_("Website"), max_length=256,
                              blank=True, null=True)
    organizer = models.CharField(verbose_name=_("Organizer"), max_length=256, blank=True)
    speaker = models.CharField(verbose_name=_("Speaker"), max_length=256, blank=True)
    type = models.ForeignKey(TouristicEventType, verbose_name=_("Type"), blank=True, null=True, on_delete=models.CASCADE)
    accessibility = models.TextField(verbose_name=_("Accessibility"), blank=True)
    participant_number = models.CharField(verbose_name=_("Number of participants"), max_length=256, blank=True)
    booking = models.TextField(verbose_name=_("Booking"), blank=True)
    target_audience = models.CharField(verbose_name=_("Target audience"), max_length=128, blank=True, null=True)
    practical_info = models.TextField(verbose_name=_("Practical info"), blank=True,
                                      help_text=_("Recommandations / To plan / Advices"))
    source = models.ManyToManyField('common.RecordSource',
                                    blank=True, related_name='touristicevents',
                                    verbose_name=_("Source"))
    portal = models.ManyToManyField('common.TargetPortal',
                                    blank=True, related_name='touristicevents',
                                    verbose_name=_("Portal"))
    eid = models.CharField(verbose_name=_("External id"), max_length=1024, blank=True, null=True)
    approved = models.BooleanField(verbose_name=_("Approved"), default=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    id_prefix = 'E'

    class Meta:
        verbose_name = _("Touristic event")
        verbose_name_plural = _("Touristic events")
        ordering = ['-begin_date']

    def __str__(self):
        return self.name

    @property
    def type1(self):
        return [self.type] if self.type else []

    @property
    def districts_display(self):
        return ', '.join([str(d) for d in self.districts])

    @property
    def dates_display(self):
        if not self.begin_date and not self.end_date:
            return ""
        elif not self.end_date:
            return _("starting from {begin}").format(
                begin=date_format(self.begin_date, 'SHORT_DATE_FORMAT'))
        elif not self.begin_date:
            return _("up to {end}").format(
                end=date_format(self.end_date, 'SHORT_DATE_FORMAT'))
        elif self.begin_date == self.end_date:
            return date_format(self.begin_date, 'SHORT_DATE_FORMAT')
        else:
            return _("from {begin} to {end}").format(
                begin=date_format(self.begin_date, 'SHORT_DATE_FORMAT'),
                end=date_format(self.end_date, 'SHORT_DATE_FORMAT'))

    @property
    def prefixed_category_id(self):
        return self.id_prefix

    def distance(self, to_cls):
        return settings.TOURISM_INTERSECTION_MARGIN

    @property
    def rando_url(self):
        category_slug = _('touristic-event')
        return '{}/{}/'.format(category_slug, self.slug)

    @property
    def meta_description(self):
        return plain_text(self.description_teaser or self.description)[:500]


TouristicEvent.add_property('touristic_contents', lambda self: intersecting(TouristicContent, self), _("Touristic contents"))
TouristicEvent.add_property('published_touristic_contents', lambda self: intersecting(TouristicContent, self).filter(published=True), _("Published touristic contents"))
Topology.add_property('touristic_events', lambda self: intersecting(TouristicEvent, self), _("Touristic events"))
Topology.add_property('published_touristic_events', lambda self: intersecting(TouristicEvent, self).filter(published=True), _("Published touristic events"))
TouristicContent.add_property('touristic_events', lambda self: intersecting(TouristicEvent, self), _("Touristic events"))
TouristicContent.add_property('published_touristic_events', lambda self: intersecting(TouristicEvent, self).filter(published=True), _("Published touristic events"))
TouristicEvent.add_property('touristic_events', lambda self: intersecting(TouristicEvent, self), _("Touristic events"))
TouristicEvent.add_property('published_touristic_events', lambda self: intersecting(TouristicEvent, self).filter(published=True), _("Published touristic events"))
