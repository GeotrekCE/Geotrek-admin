from io import BytesIO
import os
import logging
import shutil
import datetime
import hashlib

from pdfimpose import PageList

from django.conf import settings
from django.db.models import Manager as DefaultManager
from django.db import models, transaction
from django.db.models import Q
from django.db.models.fields.related import ForeignKey, ManyToManyField

from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.template.defaultfilters import slugify

from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.alias import aliases
from embed_video.backends import detect_backend, VideoDoesntExistException
from PIL.Image import DecompressionBombError

from geotrek.common.utils import classproperty

logger = logging.getLogger(__name__)


class TimeStampedModelMixin(models.Model):
    # Computed values (managed at DB-level with triggers)
    date_insert = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_("Insertion date"))
    date_update = models.DateTimeField(auto_now=True, editable=False, verbose_name=_("Update date"), db_index=True)

    class Meta:
        abstract = True

    def reload(self, fromdb):
        """Reload fields computed at DB-level (triggers)
        """
        self.date_insert = fromdb.date_insert
        self.date_update = fromdb.date_update
        return self


class NoDeleteManager(DefaultManager):
    # Use this manager when walking through FK/M2M relationships
    use_for_related_fields = True

    # Filter out deleted objects
    def existing(self):
        return self.get_queryset().filter(deleted=False)


class NoDeleteMixin(models.Model):
    deleted = models.BooleanField(editable=False, default=False, verbose_name=_("Deleted"))
    objects = NoDeleteManager()

    def delete(self, force=False, using=None, **kwargs):
        if force:
            super(NoDeleteMixin, self).delete(using, **kwargs)
        else:
            self.deleted = True
            self.save(using=using)

    class Meta:
        abstract = True

    def reload(self, fromdb):
        """Reload fields computed at DB-level (triggers)
        """
        self.deleted = fromdb.deleted
        return self


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
        return self.attachments.filter(is_image=True).exclude(title='mapimage').order_by('-starred', 'attachment_file')

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

    def serializable_pictures_mobile(self, root_pk):
        serialized = []
        if self.resized_pictures:
            first_picture = self.resized_pictures[0][0]
            thdetail_first = self.resized_pictures[0][1]
            serialized.append({
                'author': first_picture.author,
                'title': first_picture.title,
                'legend': first_picture.legend,
                'url': os.path.join('/', str(root_pk), settings.MEDIA_URL[1:], thdetail_first.name),
            })
        return serialized

    @property
    def resized_pictures(self):
        resized = []
        for picture in self.pictures:
            thumbnailer = get_thumbnailer(picture.attachment_file)
            try:
                # Uppercase options aren't used by prepared options (a primary
                # use of prepared options is to generate the filename -- these
                # options don't alter the filename).
                text = settings.THUMBNAIL_COPYRIGHT_FORMAT.format(author=picture.author, title=picture.title,
                                                                  legend=picture.legend)
                ali = thumbnailer.get_options({'size': (800, 800),
                                               'TEXT': text,
                                               'SIZE_WATERMARK': settings.THUMBNAIL_COPYRIGHT_SIZE,
                                               'watermark': hashlib.md5(text.encode('utf-8')).hexdigest()
                                               })

                thdetail = thumbnailer.get_thumbnail(ali)
            except (IOError, InvalidImageFormatError, DecompressionBombError) as e:
                logger.info(_("Image {} invalid or missing from disk: {}.").format(picture.attachment_file, e))
            else:
                resized.append((picture, thdetail))
        return resized

    @property
    def picture_print(self):
        for picture in self.pictures:
            thumbnailer = get_thumbnailer(picture.attachment_file)
            try:
                thumbnail = thumbnailer.get_thumbnail(aliases.get('print'))
            except (IOError, InvalidImageFormatError, DecompressionBombError) as e:
                logger.info(_("Image {} invalid or missing from disk: {}.").format(picture.attachment_file, e))
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
            except (IOError, InvalidImageFormatError, DecompressionBombError) as e:
                logger.info(_("Image {} invalid or missing from disk: {}.").format(picture.attachment_file, e))
                continue
            thumbnail.author = picture.author
            thumbnail.legend = picture.legend
            return thumbnail
        return None

    def resized_picture_mobile(self, root_pk):
        pictures = self.serializable_pictures_mobile(root_pk)
        if pictures:
            return pictures[0]
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
            video.is_secure = True
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
        return self.attachments.exclude(Q(is_image=True) | Q(attachment_file='')).order_by('-starred')

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
    published = models.BooleanField(verbose_name=_("Published"), default=False,
                                    help_text=_("Visible on Geotrek-rando"))
    publication_date = models.DateField(verbose_name=_("Publication date"),
                                        null=True, blank=True, editable=False)

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

        for language in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']:
            if getattr(self, 'published_%s' % language[0], False):
                return True
        return False

    @property
    def published_status(self):
        """Returns the publication status by language.
        """
        status = []
        for language in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']:
            if settings.PUBLISHED_BY_LANG:
                published = getattr(self, 'published_%s' % language[0], None) or False
            else:
                published = self.published
            status.append({
                'lang': language[0],
                'language': language[1],
                'status': published
            })
        return status

    @property
    def published_langs(self):
        """Returns languages in which the object is published.
        """
        langs = [language[0] for language in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']]
        if settings.PUBLISHED_BY_LANG:
            return [language for language in langs if getattr(self, 'published_%s' % language, None)]
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
    name = models.CharField(verbose_name=_("Name"), max_length=128,
                            help_text=_("Public name (Change carefully)"))
    review = models.BooleanField(verbose_name=_("Waiting for publication"),
                                 default=False)

    class Meta:
        abstract = True

    @property
    def slug(self):
        return slugify(self.name.lower().replace("œ", "oe")) or str(self.pk)

    @property
    def name_display(self):
        s = '<a data-pk="%s" href="%s" title="%s">%s</a>' % (self.pk,
                                                             self.get_detail_url(),
                                                             self.name,
                                                             self.name)
        if self.published:
            s = '<span class="badge badge-success" title="%s">&#x2606;</span> ' % _("Published") + s
        elif self.review:
            s = '<span class="badge badge-warning" title="%s">&#x2606;</span> ' % _("Waiting for publication") + s
        return s

    @property
    def name_csv_display(self):
        return self.name

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
        picture = self.attachments.filter(is_image=True, title='mapimage').first()
        if picture:
            attached = picture.attachment_file
            src = os.path.join(settings.MEDIA_ROOT, attached.name)
            dst = self.get_map_image_path()
            shutil.copyfile(src, dst)
        else:
            super(PublishableMixin, self).prepare_map_image(rooturl)

    def is_public(self):
        return self.any_published


class PictogramMixin(models.Model):
    pictogram = models.FileField(verbose_name=_("Pictogram"), upload_to=settings.UPLOAD_DIR,
                                 max_length=512, null=True)

    class Meta:
        abstract = True

    def pictogram_img(self):
        return mark_safe('<img src="%s" class="pictogram_%s"/>' % (self.pictogram.url,
                                                                   os.path.splitext(self.pictogram.name)[1][1:])
                         if self.pictogram else "No pictogram")

    pictogram_img.short_description = _("Pictogram")

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


def transform_pdf_booklet_callback(response):
    content = response.content
    content_b = BytesIO(content)
    import pdfimpose

    pages = PageList([content_b])
    for x in pages:
        x.pdf.strict = False
    new_pdf = pdfimpose._legacy_pypdf_impose(
        matrix=pdfimpose.ImpositionMatrix([pdfimpose.Direction.horizontal], 'left'),
        pages=pages,
        last=0
    )
    result = BytesIO()
    new_pdf.write(result)
    response.content = result.getvalue()


@transaction.atomic
def apply_merge(modeladmin, request, queryset):
    main = queryset[0]
    tail = queryset[1:]
    if not tail:
        return
    name = ' + '.join(queryset.values_list(modeladmin.merge_field, flat=True))
    fields = main._meta.get_fields()

    for field in fields:
        if field.remote_field:
            remote_field = field.remote_field.name
            if isinstance(field.remote_field, ForeignKey):
                field.remote_field.model.objects.filter(**{'%s__in' % remote_field: tail}).update(**{remote_field: main})
            elif isinstance(field.remote_field, ManyToManyField):
                for element in field.remote_field.model.objects.filter(**{'%s__in' % remote_field: tail}):
                    getattr(element, remote_field).add(main)
    max_length = main._meta.get_field(modeladmin.merge_field).max_length
    name = name if not len(name) > max_length - 4 else '%s ...' % name[:max_length - 4]
    setattr(main, modeladmin.merge_field, name)
    main.save()
    for element_to_delete in tail:
        element_to_delete.delete()


apply_merge.short_description = _('Merge')


class MergeActionMixin(object):
    actions = [apply_merge, ]
