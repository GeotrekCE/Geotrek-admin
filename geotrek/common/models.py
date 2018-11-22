import os
from PIL import Image

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from paperclip.models import FileType as BaseFileType, Attachment as BaseAttachment

from geotrek.authent.models import StructureOrNoneRelated
from geotrek.common.mixins import PictogramMixin, OptionalPictogramMixin


class Organism(StructureOrNoneRelated):

    organism = models.CharField(max_length=128, verbose_name=_("Organism"), db_column='organisme')

    class Meta:
        db_table = 'm_b_organisme'
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
        db_table = 'fl_b_fichier'

    @classmethod
    def objects_for(cls, request):
        """Override this method to filter form choices depending on structure.
        """
        return cls.for_user(request.user)

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.type, self.structure.name)
        return self.type


class Attachment(BaseAttachment):
    class Meta(BaseAttachment.Meta):
        db_table = 'fl_t_fichier'


class Theme(PictogramMixin):

    label = models.CharField(verbose_name=_("Label"), max_length=128, db_column='theme')
    cirkwi = models.ForeignKey('cirkwi.CirkwiTag', verbose_name=_("Cirkwi tag"), null=True, blank=True)

    class Meta:
        db_table = 'o_b_theme'
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
        return open(output)


class RecordSource(OptionalPictogramMixin):

    name = models.CharField(verbose_name=_("Name"), max_length=50)
    website = models.URLField(verbose_name=_("Website"), max_length=256,
                              db_column='website', blank=True, null=True)

    class Meta:
        db_table = 'o_b_source_fiche'
        verbose_name = _("Record source")
        verbose_name_plural = _("Record sources")
        ordering = ['name']

    def __str__(self):
        return self.name


class TargetPortal(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=50, unique="True", help_text=_("Used for sync"))
    website = models.URLField(verbose_name=_("Website"), max_length=256,
                              db_column='website', unique="True")

    class Meta:
        db_table = 'o_b_target_portal'
        verbose_name = _("Target portal")
        verbose_name_plural = _("Target portals")
        ordering = ('name',)

    def __str__(self):
        return self.name
