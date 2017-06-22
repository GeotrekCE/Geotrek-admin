# -*- coding: utf-8 -*-
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
from embed_video.backends import detect_backend, VideoDoesntExistException

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
        all_attachments = self.attachments.all().order_by('-starred', 'attachment_file')
        return [a for a in all_attachments if a.is_image and a.title != 'mapimage']

    @pictures.setter
    def pictures(self, values):
        self._pictures = values

    @property
    def serializable_pictures(self):
        serialized = []
        for picture, thdetail in self.resized_pictures:
            serialized.append({
                'author': picture.author,
                'title': picture.title,
                'legend': picture.legend,
                'url': os.path.join(settings.MEDIA_URL, thdetail.name),
            })
        return serialized

    @property
    def resized_pictures(self):
        resized = []
        for picture in self.pictures:
            thumbnailer = get_thumbnailer(picture.attachment_file)
            try:
                thdetail = thumbnailer.get_thumbnail(aliases.get('medium'))
            except InvalidImageFormatError:
                logger.info(_("Image %s invalid or missing from disk.") % picture.attachment_file)
            else:
                resized.append((picture, thdetail))
        return resized

    @property
    def picture_print(self):
        for picture in self.pictures:
            thumbnailer = get_thumbnailer(picture.attachment_file)
            try:
                thumbnail = thumbnailer.get_thumbnail(aliases.get('print'))
            except InvalidImageFormatError:
                logger.info(_("Image %s invalid or missing from disk.") % picture.attachment_file)
                continue
            thumbnail.author = picture.author
            thumbnail.legend = picture.legend
            return thumbnail
        return None

    @property
    def thumbnail(self):
        for picture in self.pictures:
            thumbnailer = get_thumbnailer(picture.attachment_file)
            try:
                thumbnail = thumbnailer.get_thumbnail(aliases.get('small-square'))
            except InvalidImageFormatError:
                logger.info(_("Image %s invalid or missing from disk.") % picture.attachment_file)
                continue
            thumbnail.author = picture.author
            thumbnail.legend = picture.legend
            return thumbnail
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

    @property
    def videos(self):
        all_attachments = self.attachments.all().order_by('-starred')
        return all_attachments.exclude(attachment_video='')

    @property
    def serializable_videos(self):
        serialized = []
        for att in self.videos:
            video = detect_backend(att.attachment_video)
            try:
                serialized.append({
                    'author': att.author,
                    'title': att.title,
                    'legend': att.legend,
                    'backend': type(video).__name__.replace('Backend', ''),
                    'url': video.get_url(),
                    'code': video.code,
                })
            except VideoDoesntExistException:
                pass
        return serialized

    @property
    def files(self):
        all_attachments = self.attachments.all().order_by('-starred')
        all_attachments = all_attachments.exclude(attachment_file='')
        return [a for a in all_attachments if not a.is_image]

    @property
    def serializable_files(self):
        serialized = []
        for att in self.files:
            serialized.append({
                'author': att.author,
                'title': att.title,
                'legend': att.legend,
                'url': att.attachment_file.url,
            })
        return serialized


class BasePublishableMixin(models.Model):
    """ Basic fields to control publication of objects.

    It is used for flat pages and publishable entities.
    """
    published = models.BooleanField(verbose_name=_(u"Published"), default=False,
                                    help_text=_(u"Online"), db_column='public')
    publication_date = models.DateField(verbose_name=_(u"Publication date"),
                                        null=True, blank=True, editable=False,
                                        db_column='date_publication')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.publication_date is None and self.any_published:
            self.publication_date = datetime.date.today()
        if self.publication_date is not None and not self.any_published:
            self.publication_date = None
        super(BasePublishableMixin, self).save(*args, **kwargs)

    @property
    def any_published(self):
        """Returns True if the object is published in at least one of the language
        """
        if not settings.PUBLISHED_BY_LANG:
            return self.published

        for l in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']:
            if getattr(self, 'published_%s' % l[0], False):
                return True
        return False

    @property
    def published_status(self):
        """Returns the publication status by language.
        """
        status = []
        for l in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']:
            if settings.PUBLISHED_BY_LANG:
                published = getattr(self, 'published_%s' % l[0], None) or False
            else:
                published = self.published
            status.append({
                'lang': l[0],
                'language': l[1],
                'status': published
            })
        return status

    @property
    def published_langs(self):
        """Returns languages in which the object is published.
        """
        langs = [l[0] for l in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']]
        if settings.PUBLISHED_BY_LANG:
            return [l for l in langs if getattr(self, 'published_%s' % l, None)]
        elif self.published:
            return langs
        else:
            return []


class PublishableMixin(BasePublishableMixin):
    """A mixin that contains all necessary stuff to publish objects
    (e.g. on Geotrek-rando).

    It will only work with MapEntity models.

    Initially, it was part of the ``trekking.Trek`` class. But now, all kinds of information
    can be published (c.f. PN Cevennes project).
    """
    name = models.CharField(verbose_name=_(u"Name"), max_length=128,
                            help_text=_(u"Public name (Change carefully)"), db_column='nom')
    review = models.BooleanField(verbose_name=_(u"Waiting for publication"),
                                 default=False, db_column='relecture')

    class Meta:
        abstract = True

    @property
    def slug(self):
        return slugify(self.name.lower().replace(u"œ", u"oe")) or str(self.pk)

    @property
    def name_display(self):
        s = u'<a data-pk="%s" href="%s" title="%s">%s</a>' % (self.pk,
                                                              self.get_detail_url(),
                                                              self.name,
                                                              self.name)
        if self.published:
            s = u'<span class="badge badge-success" title="%s">&#x2606;</span> ' % _("Published") + s
        elif self.review:
            s = u'<span class="badge badge-warning" title="%s">&#x2606;</span> ' % _("Waiting for publication") + s
        return s

    @property
    def name_csv_display(self):
        return unicode(self.name)

    @models.permalink
    def get_document_public_url(self):
        raise NotImplementedError

    def is_complete(self):
        """It should also have a description, etc.
        """
        modelname = self.__class__._meta.object_name.lower()
        mandatory = settings.COMPLETENESS_FIELDS.get(modelname, [])
        for f in mandatory:
            if not getattr(self, f):
                return False
        return True

    def is_publishable(self):
        return self.is_complete() and self.has_geom_valid()

    def has_geom_valid(self):
        return self.geom is not None

    def prepare_map_image(self, rooturl):
        """
        We override the default behaviour of map image preparation :
        if the object has a attached picture file with *title* ``mapimage``, we use it
        as a screenshot.
        TODO: remove this when screenshots are bullet-proof ?
        """
        attached = None
        for picture in [a for a in self.attachments.all() if a.is_image]:
            if picture.title == 'mapimage':
                attached = picture.attachment_file
                break
        if attached is None:
            super(PublishableMixin, self).prepare_map_image(rooturl)
        else:
            # Copy it along other screenshots
            src = os.path.join(settings.MEDIA_ROOT, attached.name)
            dst = self.get_map_image_path()
            shutil.copyfile(src, dst)

    def get_geom_aspect_ratio(self):
        """ Force object aspect ratio to fit height and width of
        image in public document.
        """
        modelname = self.__class__._meta.object_name.lower()
        s = settings.EXPORT_MAP_IMAGE_SIZE[modelname]
        return float(s[0]) / s[1]

    def get_attachment_print(self):
        """
        Look in attachment if there is document to be used as print version
        """
        overriden = self.attachments.filter(title="docprint").get()
        # Must have OpenOffice document mimetype
        if overriden.mimetype != ['application', 'vnd.oasis.opendocument.text']:
            raise overriden.DoesNotExist()
        return os.path.join(settings.MEDIA_ROOT, overriden.attachment_file.name)

    def is_public(self):
        return self.any_published


class PictogramMixin(models.Model):
    pictogram = models.FileField(verbose_name=_(u"Pictogram"), upload_to=settings.UPLOAD_DIR,
                                 db_column='picto', max_length=512, null=True)

    class Meta:
        abstract = True

    def pictogram_img(self):
        return u'<img src="%s" />' % (self.pictogram.url if self.pictogram else "")
    pictogram_img.short_description = _("Pictogram")
    pictogram_img.allow_tags = True

    def get_pictogram_url(self):
        return self.pictogram.url if self.pictogram else None


class OptionalPictogramMixin(PictogramMixin):
    class Meta:
        abstract = True


OptionalPictogramMixin._meta.get_field('pictogram').blank = True


class AddPropertyMixin(object):
    @classmethod
    def add_property(cls, name, func, verbose_name):
        if hasattr(cls, name):
            raise AttributeError("%s has already an attribute %s" % (cls, name))
        setattr(cls, name, property(func))
        setattr(cls, '%s_verbose_name' % name, verbose_name)
