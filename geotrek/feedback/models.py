import html
import logging
from datetime import timedelta

from colorfield.fields import ColorField

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.core.mail import send_mail
from django.db.models.query_utils import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _
from mapentity.models import MapEntityMixin

from geotrek.common.mixins import (AddPropertyMixin, NoDeleteMixin,
                                   PicturesMixin, TimeStampedModelMixin)
from geotrek.common.utils import intersecting
from geotrek.maintenance.models import Intervention
from geotrek.trekking.models import POI, Service, Trek

from .helpers import SuricateMessenger, send_report_to_managers

logger = logging.getLogger(__name__)


# This dict stores status changes that send an email and an API request
NOTIFY_SURICATE_AND_SENTINEL = {
    'filed': ['classified', 'waiting'],
    'solved_intervention': ['resolved']
}

STATUS_WHEN_REPORT_IS_LATE = {
    'waiting': 'late_intervention',
    'programmed': 'late_resolution',
}


def status_default():
    """Set status to New by default"""
    new_status_query = ReportStatus.objects.filter(label="Nouveau")
    if new_status_query:
        return new_status_query.get().pk
    return None


class SelectableUserManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(userprofile__isnull=False)


class SelectableUser(User):

    objects = SelectableUserManager()

    class Meta:
        proxy = True

    def __str__(self):
        return f"{self.username} ({self.email})"


class Report(MapEntityMixin, PicturesMixin, TimeStampedModelMixin, NoDeleteMixin, AddPropertyMixin):
    """User reports, submitted via *Geotrek-rando* or parsed from Suricate API."""

    email = models.EmailField(verbose_name=_("Email"))
    comment = models.TextField(blank=True, default="", verbose_name=_("Comment"))
    activity = models.ForeignKey(
        "ReportActivity",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Activity"),
    )
    category = models.ForeignKey(
        "ReportCategory",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Category"),
    )
    problem_magnitude = models.ForeignKey(
        "ReportProblemMagnitude",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("Problem magnitude"),
    )
    status = models.ForeignKey(
        "ReportStatus",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=status_default,
        verbose_name=_("Status"),
    )
    geom = models.PointField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_("Location"),
        srid=settings.SRID,
    )
    related_trek = models.ForeignKey(
        Trek,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_("Related trek"),
    )
    created_in_suricate = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Creation date in Suricate")
    )
    uid = models.UUIDField(
        unique=True, verbose_name=_("Identifier"), blank=True, null=True
    )
    locked = models.BooleanField(default=False, verbose_name=_("Locked"))
    origin = models.CharField(
        blank=True, null=True, default="unknown", max_length=100, verbose_name=_("Origin")
    )
    last_updated_in_suricate = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Last updated in Suricate")
    )
    assigned_user = models.ForeignKey(
        SelectableUser,
        blank=True,
        on_delete=models.PROTECT,
        null=True,
        verbose_name=_("Supervisor"),
        related_name="reports"
    )
    uses_timers = models.BooleanField(verbose_name=_("Use timers"), default=False, help_text=_("Launch timers to alert supervisor if report is not being treated on time"))

    class Meta:
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")
        ordering = ["-date_insert"]

    def __str__(self):
        if self.email:
            return self.email
        return "Anonymous report"

    @property
    def email_display(self):
        return '<a data-pk="%s" href="%s" title="%s" >%s</a>' % (
            self.pk,
            self.get_detail_url(),
            self,
            self,
        )

    @property
    def full_url(self):
        try:
            return "{}{}".format(settings.ALLOWED_HOSTS[0], self.get_detail_url())
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
    def color(self):
        default = settings.MAPENTITY_CONFIG.get('MAP_STYLES', {}).get("detail", {}).get("color", "#ffff00")
        if not(settings.ENABLE_REPORT_COLORS_PER_STATUS) or self.status is None or self.status.color is None:
            return default
        else:
            return self.status.color

    @property
    def comment_text(self):
        return html.unescape(self.comment)

    def try_send_report_to_managers(self):
        try:
            send_report_to_managers(self)
        except Exception as e:
            logger.error("Email could not be sent to managers.")
            logger.exception(e)  # This sends an email to admins :)

    def save_no_suricate(self, *args, **kwargs):
        """Save method for No Suricate mode"""
        if self.pk is None:  # New report should alert
            self.try_send_report_to_managers()
        super().save(*args, **kwargs)  # Report updates should do nothing more

    def save_suricate_report_mode(self, *args, **kwargs):
        """Save method for Suricate Report mode"""
        if self.pk is None:  # New report should alert managers AND be sent to Suricate
            self.try_send_report_to_managers()
            SuricateMessenger().post_report(self)
        super().save(*args, **kwargs)  # Report updates should do nothing more

    def save_suricate_management_mode(self, *args, **kwargs):
        """Save method for Suricate Management mode"""
        if self.pk is None:  # This is a new report
            if self.uid is None:  # This new report comes from Rando or Admin : let Suricate handle it first, don't even save it
                SuricateMessenger().post_report(self)
            else:  # This new report comes from Suricate : save
                super().save(*args, **kwargs)
        else:  # Report updates should do nothing more
            super().save(*args, **kwargs)

    def notify_assigned_user(self, message):
        subject = str("Geotrek - Nouveau Signalement à traiter")
        message = render_to_string("feedback/affectation_email.html", {"report": self, "message": message})
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.assigned_user.email])

    def notify_late_report(self, status_id):
        subject = str("Geotrek - Signalement à traiter en retard")
        message = render_to_string(f"feedback/late_{status_id}_email.html", {"report": self})
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.assigned_user.email])

    def lock_in_suricate(self):
        SuricateMessenger().lock_alert(self.uid)

    def unlock_in_suricate(self):
        SuricateMessenger().unlock_alert(self.uid)

    def send_notifications_on_status_change(self, old_status_id, message):
        if old_status_id in NOTIFY_SURICATE_AND_SENTINEL and (self.status.suricate_id in NOTIFY_SURICATE_AND_SENTINEL[old_status_id]):
            SuricateMessenger().update_status(self.uid, self.status.suricate_id, message)
            SuricateMessenger().message_sentinel(self.uid, message)

    def save(self, *args, **kwargs):
        if not settings.SURICATE_REPORT_ENABLED and not settings.SURICATE_MANAGEMENT_ENABLED:
            self.save_no_suricate(*args, **kwargs)  # No Suricate Mode
        elif settings.SURICATE_REPORT_ENABLED and not settings.SURICATE_MANAGEMENT_ENABLED:
            self.save_suricate_report_mode(*args, **kwargs)  # Suricate Report Mode
        elif settings.SURICATE_MANAGEMENT_ENABLED:
            self.save_suricate_management_mode(*args, **kwargs)  # Suricate Management Mode

    @property
    def created_in_suricate_display(self):
        return date_format(self.created_in_suricate, "SHORT_DATETIME_FORMAT")

    @property
    def last_updated_in_suricate_display(self):
        return date_format(self.last_updated_in_suricate, "SHORT_DATETIME_FORMAT")

    @property
    def name_display(self):
        s = '<a data-pk="%s" href="%s" title="%s">%s</a>' % (self.pk,
                                                             self.get_detail_url(),
                                                             self.email,
                                                             self.email)
        return s

    def distance(self, to_cls):
        """Distance to associate this report to another class"""
        return settings.REPORT_INTERSECTION_MARGIN

    def report_interventions(self):
        report_content_type = ContentType.objects.get_for_model(Report)
        qs = Q(target_type=report_content_type, target_id=self.id)
        return Intervention.objects.existing().filter(qs).distinct('pk')

    @classmethod
    def latest_updated_by_status(cls, status_id):
        return cls.objects.existing().filter(status__suricate_id=status_id).latest('date_update').get_date_update()


Report.add_property('treks', lambda self: intersecting(Trek, self), _("Treks"))
Report.add_property('pois', lambda self: intersecting(POI, self), _("POIs"))
Report.add_property('services', lambda self: intersecting(Service, self), _("Services"))
Report.add_property('interventions', lambda self: Report.report_interventions(self), _("Interventions"))


class ReportActivity(models.Model):
    """Activity involved in report"""

    label = models.CharField(verbose_name=_("Activity"), max_length=128)
    suricate_id = models.PositiveIntegerField(
        verbose_name=_("Suricate id"), null=True, blank=True, unique=True
    )

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
        ordering = ("label",)

    def __str__(self):
        return self.label


class ReportCategory(models.Model):
    label = models.CharField(verbose_name=_("Category"), max_length=128)
    suricate_id = models.PositiveIntegerField(_("Suricate id"), null=True, blank=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ("label",)

    def __str__(self):
        return self.label


class ReportStatus(models.Model):
    label = models.CharField(verbose_name=_("Status"), max_length=128)
    suricate_id = models.CharField(
        null=True,
        blank=True,
        unique=True,
        max_length=100,
        verbose_name=_("Identifiant"),
    )
    color = ColorField(verbose_name=_("Color"), default='#444444')

    class Meta:
        verbose_name = _("Status")
        verbose_name_plural = _("Status")

    def __str__(self):
        return self.label


class ReportProblemMagnitude(models.Model):
    """Report problem magnitude"""

    label = models.CharField(verbose_name=_("Problem magnitude"), max_length=128)
    suricate_id = models.PositiveIntegerField(
        verbose_name=_("Suricate id"), null=True, blank=True, unique=True
    )
    suricate_label = models.CharField(
        verbose_name=_("Suricate label"),
        max_length=128,
        null=True, blank=True, unique=True
    )

    class Meta:
        verbose_name = _("Problem magnitude")
        verbose_name_plural = _("Problem magnitudes")
        ordering = ("id",)

    def __str__(self):
        return self.label


class AttachedMessage(models.Model):
    """Messages are attached to a report"""

    date = models.DateTimeField()
    author = models.CharField(max_length=300)
    content = models.TextField()
    suricate_id = models.IntegerField(
        null=True, blank=True, verbose_name=_("Identifiant")
    )
    type = models.CharField(max_length=100)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('suricate_id', 'date', 'report')


class TimerEvent(models.Model):
    step = models.ForeignKey(ReportStatus, on_delete=models.CASCADE, null=False, related_name="timers")
    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=False, related_name="timers")
    date_event = models.DateTimeField()
    date_notification = models.DateTimeField()
    notification_sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.report.uses_timers:
            if self.pk is None:
                self.date_event = timezone.now()
                days_nb = settings.SURICATE_MANAGEMENT_SETTINGS[f"TIMER_FOR_{self.step.suricate_id.upper()}_REPORTS_IN_DAYS"]
                self.date_notification = self.date_event + timedelta(days=days_nb)
            super().save(*args, **kwargs)
        # Don't save if report doesn't use timers

    def notify_if_needed(self):
        if not(self.notification_sent) and (timezone.now() > self.date_notification) and (self.report.status.suricate_id == self.step.suricate_id):
            self.report.notify_late_report(self.step.suricate_id)
            late_status = ReportStatus.objects.get(suricate_id=STATUS_WHEN_REPORT_IS_LATE[self.step.suricate_id])
            self.report.status = late_status
            self.report.save()
            self.notification_sent = True
            self.save()

    def is_obsolete(self):
        obsolete_notified = (timezone.now() > self.date_notification) and self.notification_sent  # Notification sent by timer
        obsolete_unused = self.report.status.suricate_id != self.step.suricate_id  # Report changed status, therefore it was dealt with in time
        return obsolete_notified or obsolete_unused


class WorkflowManager(models.Model):
    user = models.ForeignKey(SelectableUser, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Workflow Manager")
        verbose_name_plural = _("Workflow Managers")

    def __str__(self):
        return f"{self.user.username} ({self.user.email})"

    def notify(self, report):
        subject = _("Geotrek - Un Signalement est à clôturer")
        message = render_to_string("feedback/cloture_email.html", {"report": report})
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email])
