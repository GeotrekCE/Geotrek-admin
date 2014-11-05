import os
from PIL import Image

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from paperclip.models import FileType as BaseFileType

from geotrek.authent.models import StructureRelated
from geotrek.common.mixins import PictogramMixin


class Organism(StructureRelated):

    organism = models.CharField(max_length=128, verbose_name=_(u"Organism"), db_column='organisme')

    class Meta:
        db_table = 'm_b_organisme'
        verbose_name = _(u"Organism")
        verbose_name_plural = _(u"Organisms")
        ordering = ['organism']

    def __unicode__(self):
        return self.organism


class FileType(StructureRelated, BaseFileType):
    """
    Attachment FileTypes, related to structure and with custom table name.
    """
    class Meta(BaseFileType.Meta):
        db_table = 'fl_b_fichier'


class Theme(PictogramMixin):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128, db_column='theme')

    class Meta:
        db_table = 'o_b_theme'
        verbose_name = _(u"Theme")
        verbose_name_plural = _(u"Themes")
        ordering = ['label']

    def __unicode__(self):
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
        is_empty = os.path.getsize(output) == 0
        is_newer = os.path.getmtime(pictopath) > os.path.getmtime(output)
        if not os.path.exists(output) or is_empty or is_newer:
            image = Image.open(pictopath)
            w, h = image.size
            if w > h:
                image = image.crop((0, 0, w / 2, h))
            image.save(output)
        return open(output)
