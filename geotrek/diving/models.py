# coding: utf8

from math import trunc

from django.conf import settings
from django.contrib.gis.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from colorfield.fields import ColorField
from mapentity.models import MapEntityMixin

from geotrek.authent.models import StructureRelated
from geotrek.common.mixins import (NoDeleteMixin, TimeStampedModelMixin,
                                   PublishableMixin, PicturesMixin, AddPropertyMixin,
                                   PictogramMixin, OptionalPictogramMixin)
from geotrek.common.models import Theme
from geotrek.common.utils import intersecting
from geotrek.core.models import Topology


class Practice(PictogramMixin):
    name = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='nom')
    order = models.IntegerField(verbose_name=_(u"Order"), null=True, blank=True, db_column='tri',
                                help_text=_(u"Alphabetical order if blank"))
    color = ColorField(verbose_name=_(u"Color"), default='#444444', db_column='couleur',
                       help_text=_(u"Color of the practice, only used in mobile."))  # To be implemented in Geotrek-rando

    class Meta:
        db_table = 'g_b_pratique'
        verbose_name = _(u"Practice")
        verbose_name_plural = _(u"Practices")
        ordering = ['order', 'name']

    def __unicode__(self):
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
    name = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='nom')

    class Meta:
        db_table = 'g_b_difficulte'
        verbose_name = _(u"Difficulty level")
        verbose_name_plural = _(u"Difficulty levels")
        ordering = ['id']

    def __unicode__(self):
        return self.name


class Level(OptionalPictogramMixin):
    """We use an IntegerField for id, since we want to edit it in Admin.
    This column is used to order technical levels, especially in public website
    where treks are filtered by level ids.
    """
    id = models.IntegerField(primary_key=True, verbose_name=_("Order"))
    name = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='nom')
    description = models.TextField(verbose_name=_(u"Description"), blank=True, db_column='description',
                                   help_text=_(u"Complete description"))

    class Meta:
        db_table = 'g_b_niveau'
        verbose_name = _(u"Technical level")
        verbose_name_plural = _(u"Technical levels")
        ordering = ['id']

    def __unicode__(self):
        return self.name


class Dive(AddPropertyMixin, PublishableMixin, MapEntityMixin, StructureRelated,
           TimeStampedModelMixin, PicturesMixin, NoDeleteMixin):
    description_teaser = models.TextField(verbose_name=_(u"Description teaser"), blank=True,
                                          help_text=_(u"A brief summary"), db_column='chapeau')
    description = models.TextField(verbose_name=_(u"Description"), blank=True, db_column='description',
                                   help_text=_(u"Complete description"))
    owner = models.CharField(verbose_name=_(u"Owner"), max_length=256, blank=True, db_column='proprietaire')
    practice = models.ForeignKey(Practice, related_name="dives",
                                 blank=True, null=True, verbose_name=_(u"Practice"), db_column='pratique')
    departure = models.CharField(verbose_name=_(u"Departure area"), max_length=128, blank=True,
                                 db_column='depart')
    disabled_sport = models.TextField(verbose_name=_(u"Disabled sport accessibility"),
                                      db_column='handicap', blank=True)
    facilities = models.TextField(verbose_name=_(u"Facilities"), db_column='equipements', blank=True)
    difficulty = models.ForeignKey(Difficulty, related_name='dives', blank=True,
                                   null=True, verbose_name=_(u"Difficulty level"), db_column='difficulte')
    levels = models.ManyToManyField(Level, related_name='dives', blank=True,
                                    verbose_name=_(u"Technical levels"), db_table='g_r_plongee_niveau')
    depth = models.PositiveIntegerField(verbose_name=_(u"Maximum depth"), db_column='profondeur',
                                        blank=True, null=True, help_text=_("meters"))
    advice = models.TextField(verbose_name=_(u"Advice"), blank=True, db_column='recommandation',
                              help_text=_(u"Risks, danger, best period, ..."))
    themes = models.ManyToManyField(Theme, related_name="dives",
                                    db_table="g_r_plongee_theme", blank=True, verbose_name=_(u"Themes"),
                                    help_text=_(u"Main theme(s)"))
    geom = models.GeometryField(verbose_name=_(u"Location"), srid=settings.SRID)
    source = models.ManyToManyField('common.RecordSource',
                                    blank=True, related_name='dives',
                                    verbose_name=_("Source"), db_table='g_r_plongee_source')
    portal = models.ManyToManyField('common.TargetPortal',
                                    blank=True, related_name='dives',
                                    verbose_name=_("Portal"), db_table='g_r_plongee_portal')
    eid = models.CharField(verbose_name=_(u"External id"), max_length=1024, blank=True, null=True, db_column='id_externe')

    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'g_t_plongee'
        verbose_name = _(u"Dive")
        verbose_name_plural = _(u"Dives")

    def __unicode__(self):
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
        location = self.geom.transform(4326, clone=True)
        return (
            "{lat_deg}°{lat_min:02d}'{lat_sec:02d}\" {lat_card} / " +
            "{lng_deg}°{lng_min:02d}'{lng_sec:02d}\" {lng_card}"
        ).format(
            lat_deg=trunc(abs(location.y)),
            lat_min=trunc((abs(location.y) * 60) % 60),
            lat_sec=trunc((abs(location.y) * 3600) % 60),
            lat_card=_("N") if location.y >= 0 else _("S"),
            lng_deg=trunc(abs(location.x)),
            lng_min=trunc((abs(location.x) * 60) % 60),
            lng_sec=trunc((abs(location.x) * 3600) % 60),
            lng_card=_("W") if location.x >= 0 else _("E"),
        )


Topology.add_property('dives', lambda self: intersecting(Dive, self), _(u"Dives"))
Topology.add_property('published_dives', lambda self: intersecting(Dive, self).filter(published=True), _(u"Published dives"))
Dive.add_property('dives', lambda self: intersecting(Dive, self), _(u"Dives"))
Dive.add_property('published_dives', lambda self: intersecting(Dive, self).filter(published=True), _(u"Published dives"))
