from math import trunc

from django.conf import settings
from django.contrib.gis.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import get_language, ugettext as _, pgettext

from colorfield.fields import ColorField
from mapentity.models import MapEntityMixin

from geotrek.authent.models import StructureRelated
from geotrek.common.mixins import (NoDeleteMixin, TimeStampedModelMixin,
                                   PublishableMixin, PicturesMixin, AddPropertyMixin,
                                   PictogramMixin, OptionalPictogramMixin)
from geotrek.common.models import Theme
from geotrek.common.utils import intersecting
from geotrek.core.models import Topology
from geotrek.trekking.models import POI, Service, Trek


class Practice(PictogramMixin):
    name = models.CharField(verbose_name=_("Name"), max_length=128, db_column='nom')
    order = models.IntegerField(verbose_name=_("Order"), null=True, blank=True, db_column='tri',
                                help_text=_("Alphabetical order if blank"))
    color = ColorField(verbose_name=_("Color"), default='#444444', db_column='couleur',
                       help_text=_("Color of the practice, only used in mobile."))  # To be implemented in Geotrek-rando

    class Meta:
        db_table = 'g_b_pratique'
        verbose_name = _("Practice")
        verbose_name_plural = _("Practices")
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    @property
    def slug(self):
        return slugify(self.name) or str(self.pk)


class Difficulty(OptionalPictogramMixin):
    """We use an IntegerField for id, since we want to edit it in Admin.
    This column is used to order difficulty levels, especially in public website
    where treks are filtered by difficulty ids.
    """
    id = models.IntegerField(primary_key=True, verbose_name=_("Order"))
    name = models.CharField(verbose_name=_("Name"), max_length=128, db_column='nom')

    class Meta:
        db_table = 'g_b_difficulte'
        verbose_name = _("Difficulty level")
        verbose_name_plural = _("Difficulty levels")
        ordering = ['id']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Manually auto-increment ids"""
        if not self.id:
            try:
                last = self.__class__.objects.all().order_by('-id')[0]
                self.id = last.id + 1
            except IndexError:
                self.id = 1
        super(Difficulty, self).save(*args, **kwargs)


class Level(OptionalPictogramMixin):
    """We use an IntegerField for id, since we want to edit it in Admin.
    This column is used to order technical levels, especially in public website
    where treks are filtered by level ids.
    """
    id = models.IntegerField(primary_key=True, verbose_name=_("Order"))
    name = models.CharField(verbose_name=_("Name"), max_length=128, db_column='nom')
    description = models.TextField(verbose_name=_("Description"), blank=True, db_column='description',
                                   help_text=_("Complete description"))

    class Meta:
        db_table = 'g_b_niveau'
        verbose_name = _("Technical level")
        verbose_name_plural = _("Technical levels")
        ordering = ['id']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Manually auto-increment ids"""
        if not self.id:
            try:
                last = self.__class__.objects.all().order_by('-id')[0]
                self.id = last.id + 1
            except IndexError:
                self.id = 1
        super(Level, self).save(*args, **kwargs)


class Dive(AddPropertyMixin, PublishableMixin, MapEntityMixin, StructureRelated,
           TimeStampedModelMixin, PicturesMixin, NoDeleteMixin):
    description_teaser = models.TextField(verbose_name=_("Description teaser"), blank=True,
                                          help_text=_("A brief summary"), db_column='chapeau')
    description = models.TextField(verbose_name=_("Description"), blank=True, db_column='description',
                                   help_text=_("Complete description"))
    owner = models.CharField(verbose_name=_("Owner"), max_length=256, blank=True, db_column='proprietaire')
    practice = models.ForeignKey(Practice, related_name="dives",
                                 blank=True, null=True, verbose_name=_("Practice"), db_column='pratique')
    departure = models.CharField(verbose_name=_("Departure area"), max_length=128, blank=True,
                                 db_column='depart')
    disabled_sport = models.TextField(verbose_name=_("Disabled sport accessibility"),
                                      db_column='handicap', blank=True)
    facilities = models.TextField(verbose_name=_("Facilities"), db_column='equipements', blank=True)
    difficulty = models.ForeignKey(Difficulty, related_name='dives', blank=True,
                                   null=True, verbose_name=_("Difficulty level"), db_column='difficulte')
    levels = models.ManyToManyField(Level, related_name='dives', blank=True,
                                    verbose_name=_("Technical levels"), db_table='g_r_plongee_niveau')
    depth = models.PositiveIntegerField(verbose_name=_("Maximum depth"), db_column='profondeur',
                                        blank=True, null=True, help_text=_("meters"))
    advice = models.TextField(verbose_name=_("Advice"), blank=True, db_column='recommandation',
                              help_text=_("Risks, danger, best period, ..."))
    themes = models.ManyToManyField(Theme, related_name="dives",
                                    db_table="g_r_plongee_theme", blank=True, verbose_name=_("Themes"),
                                    help_text=_("Main theme(s)"))
    geom = models.GeometryField(verbose_name=_("Location"), srid=settings.SRID)
    source = models.ManyToManyField('common.RecordSource',
                                    blank=True, related_name='dives',
                                    verbose_name=_("Source"), db_table='g_r_plongee_source')
    portal = models.ManyToManyField('common.TargetPortal',
                                    blank=True, related_name='dives',
                                    verbose_name=_("Portal"), db_table='g_r_plongee_portal')
    eid = models.CharField(verbose_name=_("External id"), max_length=1024, blank=True, null=True, db_column='id_externe')

    objects = Topology.get_manager_cls(models.GeoManager)()

    category_id_prefix = 'D'

    class Meta:
        db_table = 'g_t_plongee'
        verbose_name = _("Dive")
        verbose_name_plural = _("Dives")

    def __str__(self):
        return self.name

    @property
    def rando_url(self):
        if settings.SPLIT_DIVES_CATEGORIES_BY_PRACTICE and self.practice:
            category_slug = self.practice.slug
        else:
            category_slug = _('dive')
        return '{}/{}/'.format(category_slug, self.slug)

    @property
    def wgs84_pretty(self):
        location = self.geom.centroid.transform(4326, clone=True)
        return (
            "{lat_deg}°{lat_min:02d}'{lat_sec:02d}\" {lat_card} / "
            + "{lng_deg}°{lng_min:02d}'{lng_sec:02d}\" {lng_card}"
        ).format(
            lat_deg=trunc(abs(location.y)),
            lat_min=trunc((abs(location.y) * 60) % 60),
            lat_sec=trunc((abs(location.y) * 3600) % 60),
            lat_card=pgettext("North", "N") if location.y >= 0 else pgettext("South", "S"),
            lng_deg=trunc(abs(location.x)),
            lng_min=trunc((abs(location.x) * 60) % 60),
            lng_sec=trunc((abs(location.x) * 3600) % 60),
            lng_card=pgettext("East", "E") if location.x >= 0 else pgettext("West", "W"),
        )

    def distance(self, to_cls):
        return settings.DIVING_INTERSECTION_MARGIN

    @property
    def prefixed_category_id(self):
        if settings.SPLIT_DIVES_CATEGORIES_BY_PRACTICE and self.practice:
            return '{prefix}{id}'.format(prefix=self.category_id_prefix, id=self.practice.id)
        else:
            return self.category_id_prefix

    def get_map_image_url(self):
        return reverse('diving:dive_map_image', args=[str(self.pk), get_language()])

    @classmethod
    def get_create_label(cls):
        return _("Add a new dive")


Topology.add_property('dives', lambda self: intersecting(Dive, self), _("Dives"))
Topology.add_property('published_dives', lambda self: intersecting(Dive, self).filter(published=True), _("Published dives"))
Dive.add_property('dives', lambda self: intersecting(Dive, self), _("Dives"))
Dive.add_property('published_dives', lambda self: intersecting(Dive, self).filter(published=True), _("Published dives"))
Dive.add_property('treks', lambda self: intersecting(Trek, self), _("Treks"))
Dive.add_property('published_treks', lambda self: intersecting(Trek, self).filter(published=True), _("Published treks"))

Dive.add_property('pois', lambda self: intersecting(POI, self), _("POIs"))
Dive.add_property('published_pois', lambda self: intersecting(POI, self).filter(published=True), _("Published POIs"))

Dive.add_property('services', lambda self: intersecting(Service, self), _("Services"))
Dive.add_property('published_services', lambda self: intersecting(Service, self).filter(published=True), _("Published Services"))

if 'geotrek.tourism' in settings.INSTALLED_APPS:
    from geotrek.tourism import models as tourism_models
    tourism_models.TouristicContent.add_property('dives', lambda self: intersecting(Dive, self), _("Dives"))
    tourism_models.TouristicContent.add_property('published_dives', lambda self: intersecting(Dive, self).filter(published=True), _("Published dives"))
    tourism_models.TouristicEvent.add_property('dives', lambda self: intersecting(Dive, self), _("Dives"))
    tourism_models.TouristicEvent.add_property('published_dives', lambda self: intersecting(Dive, self).filter(published=True), _("Published dives"))

    Dive.add_property('touristic_contents', lambda self: intersecting(tourism_models.TouristicContent, self), _("Touristic contents"))
    Dive.add_property('published_touristic_contents', lambda self: intersecting(tourism_models.TouristicContent, self).filter(published=True), _("Published touristic contents"))
    Dive.add_property('touristic_events', lambda self: intersecting(tourism_models.TouristicEvent, self), _("Touristic events"))
    Dive.add_property('published_touristic_events', lambda self: intersecting(tourism_models.TouristicEvent, self).filter(published=True), _("Published touristic events"))
