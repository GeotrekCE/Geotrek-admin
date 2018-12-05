import logging

from django.conf import settings
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from geotrek.common.mixins import PicturesMixin
from mapentity.models import MapEntityMixin

from geotrek.common.mixins import TimeStampedModelMixin

from .helpers import send_report_managers


logger = logging.getLogger(__name__)


class Report(MapEntityMixin, PicturesMixin, TimeStampedModelMixin):
    """ User reports, mainly submitted via *Geotrek-rando*.
    """
    name = models.CharField(verbose_name=_(u"Name"), max_length=256)
    email = models.EmailField(verbose_name=_(u"Email"))
    comment = models.TextField(blank=True,
                               default="",
                               verbose_name=_(u"Comment"))
    category = models.ForeignKey('ReportCategory',
                                 null=True,
                                 blank=True,
                                 default=None,
                                 verbose_name=_(u"Category"))
    status = models.ForeignKey('ReportStatus',
                               null=True,
                               blank=True,
                               default=None,
                               verbose_name=_(u"Status"))
    geom = gis_models.PointField(null=True,
                                 blank=True,
                                 default=None,
                                 verbose_name=_(u"Location"),
                                 srid=settings.SRID)
    context_content_type = models.ForeignKey(ContentType,
                                             null=True,
                                             blank=True,
                                             editable=False)
    context_object_id = models.PositiveIntegerField(null=True,
                                                    blank=True,
                                                    editable=False)
    context_object = GenericForeignKey('context_content_type',
                                       'context_object_id')

    objects = gis_models.GeoManager()

    class Meta:
        db_table = 'f_t_signalement'
        verbose_name = _(u"Report")
        verbose_name_plural = _(u"Reports")
        ordering = ['-date_insert']

    def __unicode__(self):
        return self.name

    @property
    def name_display(self):
        return u'<a data-pk="%s" href="%s" title="%s" >%s</a>' % (self.pk,
                                                                  self.get_detail_url(),
                                                                  self,
                                                                  self)

    @classmethod
    def get_create_label(cls):
        return _(u"Add a new feedback")

    @property
    def geom_wgs84(self):
        return self.geom.transform(4326, clone=True)


@receiver(post_save, sender=Report, dispatch_uid="on_report_created")
def on_report_saved(sender, instance, created, **kwargs):
    """ Send an email to managers when a report is created.
    """
    if not created:
        return
    try:
        send_report_managers(instance)
    except Exception as e:
        logger.error('Email could not be sent to managers.')
        logger.exception(e)  # This sends an email to admins :)


class ReportCategory(models.Model):
    category = models.CharField(verbose_name=_(u"Category"),
                                max_length=128)

    class Meta:
        db_table = 'f_b_categorie'
        verbose_name = _(u"Category")
        verbose_name_plural = _(u"Categories")

    def __unicode__(self):
        return self.category


class ReportStatus(models.Model):
    status = models.CharField(verbose_name=_(u"Status"),
                              max_length=128)

    class Meta:
        db_table = 'f_b_status'
        verbose_name = _(u"Status")
        verbose_name_plural = _(u"Status")

    def __unicode__(self):
        return self.status
