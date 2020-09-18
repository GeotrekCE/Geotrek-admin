import os
from PIL import Image

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from paperclip.models import FileType as BaseFileType, Attachment as BaseAttachment

from geotrek.authent.models import StructureOrNoneRelated
from geotrek.common.mixins import PictogramMixin, OptionalPictogramMixin


class Organism(StructureOrNoneRelated):

    organism = models.CharField(max_length=128, verbose_name=_("Organism"))

    class Meta:
        verbose_name = _("Organism")
        verbose_name_plural = _("Organisms")
        ordering = ['organism']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.organism, self.structure.name)
        return self.organism


class FileType(StructureOrNoneRelated, BaseFileType):
    """
    Attachment FileTypes, related to structure and with custom table name.
    """
    class Meta(BaseFileType.Meta):
        pass

    @classmethod
    def objects_for(cls, request):
        """Override this method to filter form choices depending on structure.
        """
        return cls.objects.filter(Q(structure=request.user.profile.structure) | Q(structure=None))

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.type, self.structure.name)
        return self.type


class Attachment(BaseAttachment):

    creation_date = models.DateField(verbose_name=_("Creation Date"), null=True, blank=True)


class Theme(PictogramMixin):

    label = models.CharField(verbose_name=_("Label"), max_length=128)
    cirkwi = models.ForeignKey('cirkwi.CirkwiTag', verbose_name=_("Cirkwi tag"), null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Theme")
        verbose_name_plural = _("Themes")
        ordering = ['label']

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
        output = os.path.join(settings.MEDIA_ROOT, pictogram + '_off' + ext)

        # Recreate only if necessary !
        # is_empty = os.path.getsize(output) == 0
        # is_newer = os.path.getmtime(pictopath) > os.path.getmtime(output)
        if not os.path.exists(output):
            #  or is_empty or is_newer:
            image = Image.open(pictopath)
            w, h = image.size
            if w > h:
                image = image.crop((0, 0, w / 2, h))
            image.save(output)
        return open(output, 'rb')


class RecordSource(OptionalPictogramMixin):

    name = models.CharField(verbose_name=_("Name"), max_length=50)
    website = models.URLField(verbose_name=_("Website"), max_length=256, blank=True, null=True)

    class Meta:
        verbose_name = _("Record source")
        verbose_name_plural = _("Record sources")
        ordering = ['name']

    def __str__(self):
        return self.name


class TargetPortal(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=50, unique=True, help_text=_("Used for sync"))
    website = models.URLField(verbose_name=_("Website"), max_length=256, unique=True)
    title = models.CharField(verbose_name=_("Title Rando"), max_length=50, help_text=_("Title on Geotrek Rando"))
    description = models.TextField(verbose_name=_("Description"), help_text=_("Description on Geotrek Rando"),
                                   default='')
    facebook_id = models.CharField(verbose_name=_("Facebook ID"), max_length=20,
                                   help_text=_("Facebook ID for Geotrek Rando"), null=True, blank=True)
    facebook_image_url = models.CharField(verbose_name=_("Facebook image url"), max_length=256,
                                          help_text=_("Url of the facebook image"), default=settings.FACEBOOK_IMAGE)
    facebook_image_width = models.IntegerField(verbose_name=_("Facebook image width"),
                                               help_text=_("Facebook image's width"),
                                               default=settings.FACEBOOK_IMAGE_WIDTH)
    facebook_image_height = models.IntegerField(verbose_name=_("Facebook image height"),
                                                help_text=_("Facebook image's height"),
                                                default=settings.FACEBOOK_IMAGE_HEIGHT)

    class Meta:
        verbose_name = _("Target portal")
        verbose_name_plural = _("Target portals")
        ordering = ('name',)

    def __str__(self):
        return self.name


class ReservationSystem(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=256,
                            blank=False, null=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Reservation system")
        verbose_name_plural = _("Reservation systems")
        ordering = ('name',)
