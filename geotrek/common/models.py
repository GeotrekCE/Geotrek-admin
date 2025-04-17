import os
import random
import string
import uuid

from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from mapentity.models import MapEntityMixin
from paperclip.models import Attachment as BaseAttachment
from paperclip.models import FileType as BaseFileType
from paperclip.models import License as BaseLicense
from paperclip.validators import FileMimetypeValidator
from PIL import Image

from geotrek.authent.models import StructureOrNoneRelated

from .managers import AccessibilityAttachmentManager
from .mixins.models import OptionalPictogramMixin, PictogramMixin, TimeStampedModelMixin


def attachment_accessibility_upload(instance, filename):
    """Stores the attachment in a "per module/appname/primary key" folder"""
    _, name = os.path.split(filename)
    name, ext = os.path.splitext(name)
    renamed = slugify(name) + ext
    return "attachments_accessibility/%s/%s/%s" % (
        "%s_%s"
        % (
            instance.content_object._meta.app_label,
            instance.content_object._meta.model_name,
        ),
        instance.content_object.pk,
        renamed,
    )


class License(StructureOrNoneRelated, BaseLicense):
    class Meta(BaseLicense.Meta):
        verbose_name = _("Attachment license")
        verbose_name_plural = _("Attachment licenses")
        ordering = ["label"]


class AccessibilityAttachment(TimeStampedModelMixin):
    # Do not forget to change default value in sql (geotrek/common/sql/post_30_attachments.sql)
    class InfoAccessibilityChoices(models.TextChoices):
        SLOPE = "slope", _("Slope")
        WIDTH = "width", _("Width")
        SIGNAGE = "signage", _("Signage")

    objects = AccessibilityAttachmentManager()

    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    attachment_accessibility_file = models.ImageField(
        _("Image"),
        blank=True,
        upload_to=attachment_accessibility_upload,
        max_length=512,
        null=False,
        validators=[FileMimetypeValidator()],
    )
    info_accessibility = models.CharField(
        verbose_name=_("Information accessibility"),
        max_length=7,
        choices=InfoAccessibilityChoices.choices,
        default=InfoAccessibilityChoices.SLOPE,
    )
    license = models.ForeignKey(
        settings.PAPERCLIP_LICENSE_MODEL,
        verbose_name=_("License"),
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_attachments_accessibility",
        verbose_name=_("Creator"),
        help_text=_("User that uploaded"),
        on_delete=models.PROTECT,
    )
    author = models.CharField(
        blank=True,
        default="",
        max_length=128,
        verbose_name=_("Author"),
        help_text=_("Original creator"),
    )
    title = models.CharField(
        blank=True,
        default="",
        max_length=128,
        verbose_name=_("Filename"),
        help_text=_("Renames the file"),
    )
    legend = models.CharField(
        blank=True,
        default="",
        max_length=128,
        verbose_name=_("Legend"),
        help_text=_("Details displayed"),
    )
    random_suffix = models.CharField(null=False, blank=True, default="", max_length=128)

    class Meta:
        ordering = ["-date_insert"]
        verbose_name = _("Attachment accessibility")
        verbose_name_plural = _("Attachments accessibility")
        default_permissions = ()

    def __str__(self):
        return f"{self.creator.username} attached {self.attachment_accessibility_file.name}"

    def save(self, *args, **kwargs):
        force_refresh_suffix = kwargs.pop("force_refresh_suffix", False)
        if self.attachment_accessibility_file:
            if self.pk is None or force_refresh_suffix:
                self.random_suffix = None
                name = self.prepare_file_suffix()
                self.attachment_accessibility_file.name = (
                    attachment_accessibility_upload(self, name)
                )
        super().save(*args, **kwargs)

    @property
    def info_accessibility_display(self):
        return self.get_info_accessibility_display()

    @property
    def filename(self):
        return os.path.split(self.attachment_accessibility_file.name)[1]

    def prepare_file_suffix(self, basename=None):
        """Add random file suffix and return new filename to use in attachment_accessibility_file.save"""
        if self.attachment_accessibility_file or basename:
            if not self.random_suffix:
                # Create random suffix
                # #### /!\ If you change this line, make sure to update 'random_suffix_regexp' method above
                self.random_suffix = "-" + "".join(
                    random.choices(
                        string.ascii_lowercase + string.digits,
                        k=settings.PAPERCLIP_RANDOM_SUFFIX_SIZE,
                    )
                )
                # #### /!\ If you change this line, make sure to update 'random_suffix_regexp' method above
                if basename:
                    _, basename = os.path.split(basename)
                    basename, ext = os.path.splitext(basename)
                else:
                    _, name = os.path.split(self.attachment_accessibility_file.name)
                    name, ext = os.path.splitext(name)
                subfolder = "%s/%s" % (
                    "%s_%s"
                    % (
                        self.content_object._meta.app_label,
                        self.content_object._meta.model_name,
                    ),
                    self.content_object.pk,
                )
                # Compute maximum size left for filename
                max_filename_size = (
                    self._meta.get_field("attachment_accessibility_file").max_length
                    - len("attachments_accessibility/")
                    - settings.PAPERCLIP_RANDOM_SUFFIX_SIZE
                    - len(subfolder)
                    - len(ext)
                    - 1
                )
                # In case PAPERCLIP_RANDOM_SUFFIX_SIZE is too big
                max_filename_size = max(0, max_filename_size)
                # Create new name with suffix and proper size
                name = slugify(basename or self.title or name)[:max_filename_size]
                return name + self.random_suffix + ext
            _, name = os.path.split(self.attachment_accessibility_file.name)
            return name
        return None


class Organism(TimeStampedModelMixin, StructureOrNoneRelated):
    organism = models.CharField(max_length=128, verbose_name=_("Organism"))

    class Meta:
        verbose_name = _("Organism")
        verbose_name_plural = _("Organisms")
        ordering = ["organism"]

    def __str__(self):
        if self.structure:
            return f"{self.organism} ({self.structure.name})"
        return self.organism


class FileType(StructureOrNoneRelated, TimeStampedModelMixin, BaseFileType):
    """Attachment FileTypes, related to structure and with custom table name."""

    class Meta(BaseFileType.Meta):
        pass

    @classmethod
    def objects_for(cls, request):
        """Override this method to filter form choices depending on structure."""
        return cls.objects.filter(
            Q(structure=request.user.profile.structure) | Q(structure=None)
        )

    def __str__(self):
        if self.structure:
            return f"{self.type} ({self.structure.name})"
        return self.type


class Attachment(BaseAttachment):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class Theme(TimeStampedModelMixin, PictogramMixin):
    label = models.CharField(verbose_name=_("Name"), max_length=128)
    cirkwi = models.ForeignKey(
        "cirkwi.CirkwiTag",
        verbose_name=_("Cirkwi tag"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = _("Theme")
        verbose_name_plural = _("Themes")
        ordering = ["label"]

    def __str__(self):
        return self.label

    @property
    def pictogram_off(self):
        """
        Since pictogram can be a sprite, we want to return the left part of
        the picture (crop right 50%).
        If the pictogram is a square, do not crop.
        """
        pictogram, ext = os.path.splitext(self.pictogram.name)
        pictopath = os.path.join(settings.MEDIA_ROOT, self.pictogram.name)
        output = os.path.join(settings.MEDIA_ROOT, pictogram + "_off" + ext)

        # Recreate only if necessary !
        # is_empty = os.path.getsize(output) == 0
        # is_newer = os.path.getmtime(pictopath) > os.path.getmtime(output)
        if not os.path.exists(output):
            #  or is_empty or is_newer:
            image = Image.open(pictopath)
            w, h = image.size
            if w > h:
                image = image.crop(box=(0, 0, w / 2, h))
            image.save(output)
        return open(output, "rb")


class RecordSource(TimeStampedModelMixin, OptionalPictogramMixin):
    name = models.CharField(verbose_name=_("Name"), max_length=80)
    website = models.URLField(
        verbose_name=_("Website"), max_length=256, blank=True, default=""
    )

    class Meta:
        verbose_name = _("Record source")
        verbose_name_plural = _("Record sources")
        ordering = ["name"]

    def __str__(self):
        return self.name


class TargetPortal(TimeStampedModelMixin, models.Model):
    name = models.CharField(
        verbose_name=_("Name"), max_length=50, unique=True, help_text=_("Used for sync")
    )
    website = models.URLField(verbose_name=_("Website"), max_length=256, unique=True)
    title = models.CharField(
        verbose_name=_("Title Rando"),
        max_length=50,
        help_text=_("Title on Geotrek Rando"),
        default="",
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Description on Geotrek Rando"),
        default="",
    )
    facebook_id = models.CharField(
        verbose_name=_("Facebook ID"),
        max_length=20,
        help_text=_("Facebook ID for Geotrek Rando"),
        blank=True,
        default=settings.FACEBOOK_APP_ID,
    )
    facebook_image_url = models.CharField(
        verbose_name=_("Facebook image url"),
        max_length=256,
        help_text=_("Url of the facebook image"),
        default=settings.FACEBOOK_IMAGE,
    )
    facebook_image_width = models.IntegerField(
        verbose_name=_("Facebook image width"),
        help_text=_("Facebook image's width"),
        default=settings.FACEBOOK_IMAGE_WIDTH,
    )
    facebook_image_height = models.IntegerField(
        verbose_name=_("Facebook image height"),
        help_text=_("Facebook image's height"),
        default=settings.FACEBOOK_IMAGE_HEIGHT,
    )

    class Meta:
        verbose_name = _("Target portal")
        verbose_name_plural = _("Target portals")
        ordering = ("name",)

    def __str__(self):
        return self.name


class ReservationSystem(TimeStampedModelMixin, models.Model):
    name = models.CharField(
        verbose_name=_("Name"), max_length=256, blank=False, null=False, unique=True
    )

    class Meta:
        verbose_name = _("Reservation system")
        verbose_name_plural = _("Reservation systems")
        ordering = ("name",)

    def __str__(self):
        return self.name


class Label(TimeStampedModelMixin, OptionalPictogramMixin):
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    advice = models.TextField(verbose_name=_("Advice"), blank=True)
    published = models.BooleanField(
        verbose_name=_("Published"),
        default=False,
        help_text=_("Visible on Geotrek-rando"),
    )
    filter = models.BooleanField(
        verbose_name=_("Filter"),
        default=False,
        help_text=_("Show this label as a filter in public portal"),
    )

    class Meta:
        verbose_name = _("Label")
        verbose_name_plural = _("Labels")
        ordering = ["name"]

    def __str__(self):
        return self.name


class RatingScaleMixin(TimeStampedModelMixin, models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    order = models.IntegerField(
        verbose_name=_("Order"),
        null=True,
        blank=True,
        help_text=_("Within a practice. Alphabetical order if blank"),
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name} ({self.practice.name})"


class RatingMixin(TimeStampedModelMixin, OptionalPictogramMixin, models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    description = models.TextField(verbose_name=_("Description"), blank=True)
    order = models.IntegerField(
        verbose_name=_("Order"),
        null=True,
        blank=True,
        help_text=_("Alphabetical order if blank"),
    )
    color = ColorField(verbose_name=_("Color"), blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.scale.name} : {self.name}"


class HDViewPoint(TimeStampedModelMixin, MapEntityMixin):
    picture = models.FileField(verbose_name=_("Picture"), upload_to="hdviewpoints/")
    geom = gis_models.PointField(verbose_name=_("Location"), srid=settings.SRID)
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    content_object = GenericForeignKey("content_type", "object_id")
    annotations = models.JSONField(
        verbose_name=_("Annotations"), blank=True, default=dict
    )
    annotations_categories = models.JSONField(blank=True, default=dict)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    author = models.CharField(
        blank=True,
        default="",
        max_length=128,
        verbose_name=_("Author"),
        help_text=_("Original creator"),
    )
    title = models.CharField(
        max_length=1024,
        verbose_name=_("Title"),
        help_text=_("Title for this view point"),
    )
    legend = models.CharField(
        blank=True,
        default="",
        max_length=1024,
        verbose_name=_("Legend"),
        help_text=_("Details about this view"),
    )
    license = models.ForeignKey(
        settings.PAPERCLIP_LICENSE_MODEL,
        verbose_name=_("License"),
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = _("HD View")
        verbose_name_plural = _("HD Views")
        permissions = (("read_hdviewpoint", "Can read hd view point"),)

    def __str__(self):
        return self.title

    @property
    def full_url(self):
        return reverse("common:hdviewpoint_detail", kwargs={"pk": self.pk})

    @property
    def metadata_url(self):
        return reverse("common:hdviewpoint-metadata", kwargs={"pk": self.pk})

    @classmethod
    def get_list_url(cls):
        return reverse("admin:common_hdviewpoint_changelist")

    def get_picture_tile_url(self, x, y, z):
        url = reverse(
            "common:hdviewpoint-tile",
            kwargs={"pk": self.pk, "x": x, "y": y, "z": z, "fmt": "png"},
        )
        return f"{url}?{urlencode({'source': 'vips'})}"

    def get_generic_picture_tile_url(self):
        url = self.get_picture_tile_url(0, 0, 0).replace(
            "/0/0/0.png", "/{z}/{x}/{y}.png"
        )
        return url

    @property
    def thumbnail_url(self):
        url = reverse(
            "common:hdviewpoint-thumbnail", kwargs={"pk": self.pk, "fmt": "png"}
        )
        return f"{url}?{urlencode({'source': 'vips'})}"

    def get_annotate_url(self):
        return reverse("common:hdviewpoint_annotate", args=[self.pk])


class AnnotationCategory(TimeStampedModelMixin, PictogramMixin):
    label = models.CharField(verbose_name=_("Name"), max_length=128)

    class Meta:
        verbose_name = _("Annotation category")
        verbose_name_plural = _("Annotation categories")
        ordering = ["label"]

    def __str__(self):
        return self.label


class AccessMean(TimeStampedModelMixin):
    label = models.CharField(max_length=128)

    class Meta:
        verbose_name = _("Access mean")
        verbose_name_plural = _("Access means")
        ordering = ("label",)

    def __str__(self):
        return self.label
