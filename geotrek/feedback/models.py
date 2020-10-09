import html
import logging

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from geotrek.common.mixins import PicturesMixin
from mapentity.models import MapEntityMixin

from geotrek.common.mixins import TimeStampedModelMixin
from geotrek.trekking.models import Trek

from .helpers import send_report_managers, post_report_to_suricate


logger = logging.getLogger(__name__)


def status_default():
    """Set status to New by default"""
    new_status_query = ReportStatus.objects.filter(label='Nouveau')
    if new_status_query:
        return new_status_query.get().pk
    return None


class Report(MapEntityMixin, PicturesMixin, TimeStampedModelMixin):
    """ User reports, mainly submitted via *Geotrek-rando*.
    """
    email = models.EmailField(verbose_name=_("Email"))
    comment = models.TextField(blank=True,
                               default="",
                               verbose_name=_("Comment"))
    activity = models.ForeignKey('ReportActivity',
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True,
                                 verbose_name=_("Activity"))
    category = models.ForeignKey('ReportCategory',
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True,
                                 verbose_name=_("Category"))
    problem_magnitude = models.ForeignKey('ReportProblemMagnitude',
                                          null=True,
                                          blank=True,
                                          on_delete=models.CASCADE,
                                          verbose_name=_("Problem magnitude"))
    status = models.ForeignKey('ReportStatus',
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True,
                               default=status_default,
                               verbose_name=_("Status"))
    geom = models.PointField(null=True,
                             blank=True,
                             default=None,
                             verbose_name=_("Location"),
                             srid=settings.SRID)
    related_trek = models.ForeignKey(Trek,
                                     null=True,
                                     blank=True,
                                     on_delete=models.CASCADE,
                                     verbose_name=_('Related trek'))
    context_content_type = models.ForeignKey(ContentType,
                                             on_delete=models.CASCADE,
                                             null=True,
                                             blank=True,
                                             editable=False)
    context_object_id = models.PositiveIntegerField(null=True,
                                                    blank=True,
                                                    editable=False)
    context_object = GenericForeignKey('context_content_type',
                                       'context_object_id')

    class Meta:
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")
        ordering = ['-date_insert']

    def __str__(self):
        if self.email:
            return self.email
        return "Anonymous report"

    @property
    def email_display(self):
        return '<a data-pk="%s" href="%s" title="%s" >%s</a>' % (self.pk,
                                                                 self.get_detail_url(),
                                                                 self,
                                                                 self)

    @property
    def full_url(self):
        try:
            return '{}{}'.format(
                settings.ALLOWED_HOSTS[0],
                self.get_detail_url()
            )
        except KeyError:
            # Do not display url if there is no ALLOWED_HOSTS
            return ""

    @classmethod
    def get_create_label(cls):
        return _("Add a new feedback")

    @property
    def geom_wgs84(self):
        return self.geom.transform(4326, clone=True)

    @property
    def comment_text(self):
        return html.unescape(self.comment)


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

    if settings.SURICATE_REPORT_ENABLED:
        try:
            post_report_to_suricate(instance)
        except Exception as e:
            logger.error('Report could not be sent to Suricate API.')
            logger.exception(e)


class ReportActivity(models.Model):
    """Activity involved in report"""
    label = models.CharField(verbose_name=_("Activity"),
                             max_length=128)
    suricate_id = models.PositiveIntegerField(_("Suricate id"),
                                              null=True,
                                              blank=True)

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
        ordering = ("label",)

    def __str__(self):
        return self.label


class ReportCategory(models.Model):
    label = models.CharField(verbose_name=_("Category"),
                             max_length=128)
    suricate_id = models.PositiveIntegerField(_("Suricate id"),
                                              null=True,
                                              blank=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ("label",)

    def __str__(self):
        return self.label


class ReportStatus(models.Model):
    label = models.CharField(verbose_name=_("Status"),
                             max_length=128)

    class Meta:
        verbose_name = _("Status")
        verbose_name_plural = _("Status")

    def __str__(self):
        return self.label


class ReportProblemMagnitude(models.Model):
    """Report problem magnitude"""
    label = models.CharField(verbose_name=_("Problem magnitude"),
                             max_length=128)
    suricate_id = models.PositiveIntegerField(_("Suricate id"),
                                              null=True,
                                              blank=True)

    class Meta:
        verbose_name = _("Problem magnitude")
        verbose_name_plural = _("Problem magnitudes")
        ordering = ("id",)

    def __str__(self):
        return self.label
