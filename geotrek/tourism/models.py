from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from extended_choices import Choices


DATA_SOURCE_TYPES = Choices(
    ('GEOJSON', 'GEOJSON', _("GeoJSON")),
    ('TOURINFRANCE', 'TOURINFRANCE', _("TourInFrance")),
)


class DataSource(models.Model):
    title = models.CharField(verbose_name=_(u"Title"),
                             max_length=128, db_column='titre')
    url = models.URLField(max_length=400, db_column='url')
    pictogram = models.FileField(verbose_name=_(u"Pictogram"),
                                 upload_to=settings.UPLOAD_DIR,
                                 db_column='picto', max_length=512)
    type = models.CharField(db_column="type", max_length=32,
                            choices=DATA_SOURCE_TYPES)

    def __unicode__(self):
        return self.title

    def pictogram_img(self):
        return u'<img src="%s" />' % (self.pictogram.url if self.pictogram else "")
    pictogram_img.short_description = _("Pictogram")
    pictogram_img.allow_tags = True

    class Meta:
        db_table = 't_t_source_donnees'
        verbose_name = _(u"Data source")
        verbose_name_plural = _(u"Data sources")
        ordering = ['title', 'url']
