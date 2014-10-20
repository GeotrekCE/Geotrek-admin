import os
import re
import logging

from django.contrib.gis.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import lazy

from easy_thumbnails.alias import aliases
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer
from mapentity import registry
from mapentity.serializers import smart_plain_text
from extended_choices import Choices
from multiselectfield import MultiSelectField

from geotrek.common.mixins import PictogramMixin


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
                             related_name='desks', null=True, blank=True,
                             db_column='type')
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
