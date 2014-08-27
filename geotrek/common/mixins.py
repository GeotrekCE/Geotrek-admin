import os
import logging
import shutil
import datetime

from django.conf import settings
from django.db.models import Manager as DefaultManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from easy_thumbnails.alias import aliases
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer

from geotrek.common.utils import classproperty


logger = logging.getLogger(__name__)


class TimeStampedModelMixin(models.Model):
    # Computed values (managed at DB-level with triggers)
    date_insert = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_(u"Insertion date"), db_column='date_insert')
    date_update = models.DateTimeField(auto_now=True, editable=False, verbose_name=_(u"Update date"), db_column='date_update')

    class Meta:
        abstract = True

    def reload(self, fromdb=None):
        """Reload fields computed at DB-level (triggers)
        """
        if fromdb is None:
            fromdb = self.__class__.objects.get(pk=self.pk)
        self.date_insert = fromdb.date_insert
        self.date_update = fromdb.date_update
        return self


class NoDeleteMixin(models.Model):
    deleted = models.BooleanField(editable=False, default=False, db_column='supprime', verbose_name=_(u"Deleted"))

    def delete(self, force=False, using=None, **kwargs):
        if force:
            super(NoDeleteMixin, self).delete(using, **kwargs)
        else:
            self.deleted = True
            self.save(using=using)

    class Meta:
        abstract = True

    def reload(self, fromdb=None):
        """Reload fields computed at DB-level (triggers)
        """
        if fromdb is None:
            fromdb = self.__class__.objects.get(pk=self.pk)
        self.deleted = fromdb.deleted
        return self

    @classmethod
    def get_manager_cls(cls, parent_mgr_cls=DefaultManager):

        class NoDeleteManager(parent_mgr_cls):
            # Use this manager when walking through FK/M2M relationships
            use_for_related_fields = True

            # Filter out deleted objects
            def existing(self):
                return self.get_queryset().filter(deleted=False)

        return NoDeleteManager


class PicturesMixin(object):
    """A common class to share code between Trek and POI regarding
    attached pictures"""

    @property
    def pictures(self):
        """
        Find first image among attachments.
        Since we allow screenshot to be overriden by attachments
        named 'mapimage', filter it from object pictures.
        """
        if hasattr(self, '_pictures'):
            return self._pictures
        return [a for a in self.attachments.all() if a.is_image
                and a.title != 'mapimage']

    @pictures.setter
    def pictures(self, values):
        self._pictures = values

    @property
    def serializable_pictures(self):
        serialized = []
        for picture in self.pictures:
            thumbnailer = get_thumbnailer(picture.attachment_file)
            try:
                thdetail = thumbnailer.get_thumbnail(aliases.get('medium'))
                thurl = os.path.join(settings.MEDIA_URL, thdetail.name)
            except InvalidImageFormatError:
                thurl = None
                logger.error(_("Image %s invalid or missing from disk.") % picture.attachment_file)
                pass
            serialized.append({
                'author': picture.author,
                'title': picture.title,
                'legend': picture.legend,
                'url': thurl
            })
        return serialized

    @property
    def picture_print(self):
        for picture in self.pictures:
            thumbnailer = get_thumbnailer(picture.attachment_file)
            try:
                return thumbnailer.get_thumbnail(aliases.get('print'))
            except InvalidImageFormatError:
                logger.error(_("Image %s invalid or missing from disk.") % picture.attachment_file)
                pass
        return None

    @property
    def thumbnail(self):
        for picture in self.pictures:
            thumbnailer = get_thumbnailer(picture.attachment_file)
            try:
                return thumbnailer.get_thumbnail(aliases.get('small-square'))
            except InvalidImageFormatError:
                logger.error(_("Image %s invalid or missing from disk.") % picture.attachment_file)
                pass
        return None

    @classproperty
    def thumbnail_verbose_name(cls):
        return _("Thumbnail")

    @property
    def thumbnail_display(self):
        thumbnail = self.thumbnail
        if thumbnail is None:
            return _("None")
        return '<img height="20" width="20" src="%s"/>' % os.path.join(settings.MEDIA_URL, thumbnail.name)

    @property
    def thumbnail_csv_display(self):
        return '' if self.thumbnail is None else os.path.join(settings.MEDIA_URL, self.thumbnail.name)

    @property
    def serializable_thumbnail(self):
        th = self.thumbnail
        if not th:
            return None
        return os.path.join(settings.MEDIA_URL, th.name)


class PictogramMixin(models.Model):
    pictogram = models.FileField(verbose_name=_(u"Pictogram"), upload_to=settings.UPLOAD_DIR,
                                 db_column='picto', max_length=512, null=True)

    class Meta:
        abstract = True

    @property
    def serializable_pictogram(self):
        return self.pictogram.url if self.pictogram else None

    def pictogram_img(self):
        return u'<img src="%s" />' % (self.pictogram.url if self.pictogram else "")
    pictogram_img.short_description = _("Pictogram")
    pictogram_img.allow_tags = True
