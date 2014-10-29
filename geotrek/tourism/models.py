import os
import re
import logging

from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import lazy

from easy_thumbnails.alias import aliases
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer
from mapentity import registry
from mapentity.models import MapEntityMixin
from mapentity.serializers import smart_plain_text
from modeltranslation.manager import MultilingualManager

from geotrek.authent.models import StructureRelated
from geotrek.common.mixins import (NoDeleteMixin, TimeStampedModelMixin,
                                   PictogramMixin, PublishableMixin,
                                   PicturesMixin)
from geotrek.common.models import Theme

from extended_choices import Choices
from multiselectfield import MultiSelectField


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


class DataSource(models.Model):
    title = models.CharField(verbose_name=_(u"Title"),
                             max_length=128, db_column='titre')
    url = models.URLField(max_length=400, db_column='url')
    pictogram = models.FileField(verbose_name=_(u"Pictogram"),
                                 upload_to=settings.UPLOAD_DIR,
                                 db_column='picto', max_length=512)
    type = models.CharField(db_column="type", max_length=32,
                            choices=DATA_SOURCE_TYPES)
    targets = MultiSelectField(verbose_name=_(u"Display"),
                               max_length=512,
                               choices=lazy(_get_target_choices, tuple)(), null=True, blank=True)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('tourism:datasource_geojson', [str(self.id)])

    def pictogram_img(self):
        return u'<img src="%s" />' % (self.pictogram.url if self.pictogram else "")
    pictogram_img.short_description = _("Pictogram")
    pictogram_img.allow_tags = True

    class Meta:
        db_table = 't_t_source_donnees'
        verbose_name = _(u"External data source")
        verbose_name_plural = _(u"External data sources")
        ordering = ['title', 'url']


class InformationDeskType(PictogramMixin):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128, db_column='label')

    class Meta:
        db_table = 'o_b_type_renseignement'
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

    class Meta:
        db_table = 'o_b_renseignement'
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


class TouristicContentCategory(PictogramMixin):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128, db_column='nom')
    type1_label = models.CharField(verbose_name=_(u"First list label"), max_length=128,
                                   db_column='label_type1', blank=True)
    type2_label = models.CharField(verbose_name=_(u"Second list label"), max_length=128,
                                   db_column='label_type2', blank=True)

    class Meta:
        db_table = 't_b_contenu_touristique'
        verbose_name = _(u"Touristic content category")
        verbose_name_plural = _(u"Touristic content categories")
        ordering = ['label']

    def __unicode__(self):
        return self.label


class TouristicContentType(models.Model):

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


class TouristicContent(MapEntityMixin, PublishableMixin, StructureRelated,
                       TimeStampedModelMixin, PicturesMixin, NoDeleteMixin):
    """ A generic touristic content (accomodation, museum, etc.) in the park
    """
    description_teaser = models.TextField(verbose_name=_(u"Description teaser"), blank=True,
                                          help_text=_(u"A brief summary"), db_column='chapeau')
    description = models.TextField(verbose_name=_(u"Description"), blank=True, db_column='description',
                                   help_text=_(u"Complete description"))
    themes = models.ManyToManyField(Theme, related_name="touristiccontents",
                                    db_table="o_r_contenu_touristique_theme", blank=True, null=True, verbose_name=_(u"Themes"),
                                    help_text=_(u"Main theme(s)"))
    geom = models.GeometryField(srid=settings.SRID)
    category = models.ForeignKey(TouristicContentCategory, related_name='contents',
                                 verbose_name=_(u"Category"), db_column='categorie')
    contact = models.TextField(verbose_name=_(u"Contact"), blank=True, db_column='contact')
    email = models.EmailField(verbose_name=_(u"Email"), max_length=256, db_column='email',
                              blank=True, null=True)
    website = models.URLField(verbose_name=_(u"Website"), max_length=256, db_column='website',
                              blank=True, null=True)
    practical_info = models.TextField(verbose_name=_(u"Practical info"), blank=True, db_column='infos_pratiques')
    type1 = models.ManyToManyField(TouristicContentType, related_name='contents1',
                                   verbose_name=_(u"Type 1"), db_column='type1',
                                   blank=True)
    type2 = models.ManyToManyField(TouristicContentType, related_name='contents2',
                                   verbose_name=_(u"Type 2"), db_column='type2',
                                   blank=True)

    objects = NoDeleteMixin.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 't_t_contenu_touristique'
        verbose_name = _(u"Touristic content")
        verbose_name_plural = _(u"Touristic contents")

    def __unicode__(self):
        return self.name


class TouristicEventUsage(models.Model):

    usage = models.CharField(verbose_name=_(u"Usage"), max_length=128, db_column='usage')

    class Meta:
        db_table = 'o_b_evenement_touristique_usage'
        verbose_name = _(u"Touristic event usage")
        verbose_name_plural = _(u"Touristic event usages")
        ordering = ['usage']

    def __unicode__(self):
        return self.usage


class TouristicEventPublic(models.Model):

    public = models.CharField(verbose_name=_(u"Public"), max_length=128, db_column='public')

    class Meta:
        db_table = 'o_b_evenement_touristique_public'
        verbose_name = _(u"Touristic event public")
        verbose_name_plural = _(u"Touristic event publics")
        ordering = ['public']

    def __unicode__(self):
        return self.public


class TouristicEvent(MapEntityMixin, PublishableMixin, StructureRelated,
                     PicturesMixin, TimeStampedModelMixin, NoDeleteMixin):
    """ A touristic event (conference, workshop, etc.) in the park
    """
    description_teaser = models.TextField(verbose_name=_(u"Description teaser"), blank=True,
                                          help_text=_(u"A brief summary"), db_column='chapeau')
    description = models.TextField(verbose_name=_(u"Description"), blank=True, db_column='description',
                                   help_text=_(u"Complete description"))
    themes = models.ManyToManyField(Theme, related_name="touristic_events",
                                    db_table="o_r_evenement_touristique_theme", blank=True, null=True, verbose_name=_(u"Themes"),
                                    help_text=_(u"Main theme(s)"))
    geom = models.PointField(srid=settings.SRID)
    begin_date = models.DateField(blank=True, null=True, verbose_name=_(u"Begin date"), db_column='date_debut')
    end_date = models.DateField(blank=True, null=True, verbose_name=_(u"End date"), db_column='date_fin')
    duration = models.CharField(verbose_name=_(u"Duration"), max_length=64, blank=True, db_column='duree')
    meeting_point = models.CharField(verbose_name=_(u"Meeting point"), max_length=256, blank=True, db_column='point_rdv')
    meeting_time = models.TimeField(verbose_name=_(u"Meeting time"), blank=True, null=True, db_column='heure_rdv')
    contact = models.TextField(verbose_name=_(u"Contact"), blank=True, db_column='contact')
    email = models.EmailField(verbose_name=_(u"Email"), max_length=256, db_column='email',
                              blank=True, null=True)
    website = models.URLField(verbose_name=_(u"Website"), max_length=256, db_column='website',
                              blank=True, null=True)
    organizer = models.CharField(verbose_name=_(u"Organizer"), max_length=256, blank=True, db_column='organisateur')
    speaker = models.CharField(verbose_name=_(u"Speaker"), max_length=256, blank=True, db_column='intervenant')
    usage = models.ForeignKey(TouristicEventUsage, verbose_name=_(u"Usage"), blank=True, null=True, db_column='usage')
    accessibility = models.CharField(verbose_name=_(u"Accessibility"), max_length=256, blank=True, db_column='accessibilite')
    participant_number = models.CharField(verbose_name=_(u"Number of participants"), max_length=256, blank=True, db_column='nb_places')
    booking = models.TextField(verbose_name=_(u"Booking"), blank=True, db_column='reservation')
    public = models.ForeignKey(TouristicEventPublic, verbose_name=_(u"Public"), blank=True, null=True, db_column='public_vise')
    practical_info = models.TextField(verbose_name=_(u"Practical info"), blank=True, db_column='infos_pratiques',
                                      help_text=_(u"Recommandations / To plan / Advices"))

    objects = NoDeleteMixin.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 't_t_evenement_touristique'
        verbose_name = _(u"Touristic event")
        verbose_name_plural = _(u"Touristic events")
        ordering = ['-begin_date']

    def __unicode__(self):
        return self.name
