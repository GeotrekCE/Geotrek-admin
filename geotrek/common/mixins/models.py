import datetime
import hashlib
import os
import shutil
import uuid

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.mail import mail_managers
from django.db import models
from django.db.models import Count, Max
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from easy_thumbnails.alias import aliases
from easy_thumbnails.files import get_thumbnailer
from mapentity.models import MapEntityMixin
from modeltranslation.utils import build_localized_fieldname

from geotrek.common.mixins.managers import NoDeleteManager
from geotrek.common.utils import classproperty, logger


class CheckBoxActionMixin:
    @property
    def checkbox(self):
        return f'<input type="checkbox" name="{self._meta.model_name}[]" value="{self.pk}" />'

    @classproperty
    def checkbox_verbose_name(cls):
        return _("Action")

    @property
    def checkbox_display(self):
        return self.checkbox


class TimeStampedModelMixin(models.Model):
    # Computed values (managed at DB-level with triggers)
    date_insert = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name=_("Insertion date")
    )
    date_update = models.DateTimeField(
        auto_now=True, editable=False, verbose_name=_("Update date"), db_index=True
    )

    class Meta:
        abstract = True

    def reload(self, fromdb):
        """Reload fields computed at DB-level (triggers)"""
        self.date_insert = fromdb.date_insert
        self.date_update = fromdb.date_update
        return self

    @property
    def date_insert_display(self):
        return date_format(self.date_insert, "SHORT_DATETIME_FORMAT")

    @property
    def date_update_display(self):
        return date_format(self.date_update, "SHORT_DATETIME_FORMAT")

    date_update_verbose_name = _("Update date")

    @classproperty
    def last_update_and_count(self):
        return self._meta.model.objects.aggregate(
            last_update=Max("date_update"), count=Count("pk")
        )


class NoDeleteMixin(models.Model):
    deleted = models.BooleanField(
        editable=False, default=False, verbose_name=_("Deleted")
    )
    objects = NoDeleteManager()

    class Meta:
        abstract = True

    def delete(self, force=False, using=None, **kwargs):
        if force:
            super().delete(using, **kwargs)
        else:
            self.deleted = True
            self.save(using=using)

    def reload(self, fromdb):
        """Reload fields computed at DB-level (triggers)"""
        self.deleted = fromdb.deleted
        return self


class PicturesMixin:
    """A common class to share code between Trek and POI regarding attached pictures"""

    @property
    def pictures(self):
        """
        Find first image among attachments.
        Since we allow screenshot to be overriden by attachments
        named 'mapimage', filter it from object pictures.
        """
        if hasattr(self, "_pictures"):
            return self._pictures
        return (
            self.attachments.filter(is_image=True)
            .exclude(title="mapimage")
            .order_by("-starred", "attachment_file")
        )

    @property
    def serializable_pictures(self):
        serialized = []
        for picture, thdetail in self.resized_pictures:
            serialized.append(
                {
                    "author": picture.author,
                    "title": picture.title,
                    "legend": picture.legend,
                    "url": os.path.join(settings.MEDIA_URL, thdetail.name),
                }
            )
        return serialized

    def serializable_pictures_mobile(self, root_pk):
        serialized = []
        if self.resized_pictures:
            for picture, thdetail in self.resized_pictures[
                : settings.MOBILE_NUMBER_PICTURES_SYNC
            ]:
                serialized.append(
                    {
                        "author": picture.author,
                        "title": picture.title,
                        "legend": picture.legend,
                        "url": os.path.join(
                            "/", str(root_pk), settings.MEDIA_URL[1:], thdetail.name
                        ),
                    }
                )
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
                text = settings.THUMBNAIL_COPYRIGHT_FORMAT.format(
                    author=picture.author, title=picture.title, legend=picture.legend
                )
                ali = thumbnailer.get_options(
                    {
                        "size": (800, 800),
                        "TEXT": text,
                        "SIZE_WATERMARK": settings.THUMBNAIL_COPYRIGHT_SIZE,
                        "watermark": hashlib.md5(text.encode("utf-8")).hexdigest(),
                    }
                )

                thdetail = thumbnailer.get_thumbnail(ali)
            except Exception as e:
                logger.warning(
                    "Image %s invalid or missing from disk: %s %s.",
                    picture.attachment_file,
                    type(e),
                    e,
                )
            else:
                resized.append((picture, thdetail))
        return resized

    def get_thumbnail(self, alias):
        for picture in self.pictures:
            thumbnailer = get_thumbnailer(picture.attachment_file)
            try:
                thumbnail = thumbnailer.get_thumbnail(aliases.get(alias))
            except Exception as e:
                logger.warning(
                    "Image %s invalid or missing from disk: %s %s.",
                    picture.attachment_file,
                    type(e),
                    e,
                )
                continue
            thumbnail.author = picture.author
            thumbnail.legend = picture.legend
            return thumbnail
        return None

    @property
    def picture_print(self):
        return self.get_thumbnail("print")

    @property
    def thumbnail(self):
        return self.get_thumbnail("small-square")

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
        return f'<img height="20" width="20" src="{os.path.join(settings.MEDIA_URL, thumbnail.name)}"/>'

    @property
    def sorted_attachments(self):
        return self.attachments.order_by("-starred", "date_insert")


class BasePublishableMixin(models.Model):
    """
    Basic fields to control publication of objects.
    It is used for flat pages and publishable entities.
    """

    published = models.BooleanField(
        verbose_name=_("Published"),
        default=False,
        help_text=_("Visible on Geotrek-rando"),
    )
    publication_date = models.DateField(
        verbose_name=_("Publication date"), null=True, blank=True, editable=False
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.publication_date is None and self.any_published:
            self.publication_date = datetime.date.today()
        if self.publication_date is not None and not self.any_published:
            self.publication_date = None
        super().save(*args, **kwargs)

    @property
    def any_published(self):
        """Returns True if the object is published in at least one of the language"""
        if not settings.PUBLISHED_BY_LANG:
            return self.published

        for language in settings.MAPENTITY_CONFIG["TRANSLATED_LANGUAGES"]:
            if getattr(
                self, build_localized_fieldname("published", language[0]), False
            ):
                return True
        return False

    @property
    def published_status(self):
        """Returns the publication status by language."""
        status = []
        for language in settings.MAPENTITY_CONFIG["TRANSLATED_LANGUAGES"]:
            if settings.PUBLISHED_BY_LANG:
                published = (
                    getattr(
                        self, build_localized_fieldname("published", language[0]), None
                    )
                    or False
                )
            else:
                published = self.published
            status.append(
                {"lang": language[0], "language": language[1], "status": published}
            )
        return status

    @property
    def published_langs(self):
        """Returns languages in which the object is published."""
        langs = [
            language[0]
            for language in settings.MAPENTITY_CONFIG["TRANSLATED_LANGUAGES"]
        ]
        if settings.PUBLISHED_BY_LANG:
            return [
                language
                for language in langs
                if getattr(self, build_localized_fieldname("published", language), None)
            ]
        elif self.published:
            return langs
        else:
            return []

    def is_public(self):
        return self.any_published


class PublishableMixin(BasePublishableMixin):
    """A mixin that contains all necessary stuff to publish objects
    (e.g. on Geotrek-rando).

    It will only work with MapEntity models.

    Initially, it was part of the ``trekking.Trek`` class. But now, all kinds of information
    can be published (c.f. PN Cevennes project).
    """

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=128,
        help_text=_("Public name (Change carefully)"),
    )
    review = models.BooleanField(
        verbose_name=_("Waiting for publication"), default=False
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if (
            self.pk
            and self.__class__.objects.get(pk=self.pk).review != self.review
            and self.review
        ) and settings.ALERT_REVIEW:
            subject = _("{obj} need a review").format(obj=self)
            message = render_to_string("common/review_email_message.txt", {"obj": self})
            try:
                mail_managers(subject, message, fail_silently=False)
            except Exception as exc:
                msg = f"Caught {exc.__class__.__name__}: {exc}"
                logger.warning(f"Error mail managers didn't work ({msg})")
        super().save(*args, **kwargs)

    @property
    def slug(self):
        return slugify(self.name.lower().replace("œ", "oe")) or str(self.pk)

    @property
    def name_display(self):
        s = f'<a data-pk="{self.pk}" href="{self.get_detail_url()}" title="{self.name}">{self.name}</a>'
        if self.published:
            s = (
                '<span class="badge badge-success" title="{}">&#x2606;</span> '.format(
                    _("Published")
                )
                + s
            )
        elif self.review:
            s = (
                '<span class="badge badge-warning" title="{}">&#x2606;</span> '.format(
                    _("Waiting for publication")
                )
                + s
            )
        return s

    @property
    def name_csv_display(self):
        return self.name

    def is_complete(self):
        """It should also have a description, etc."""
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
        picture = self.attachments.filter(is_image=True, title="mapimage").first()
        if picture:
            attached = picture.attachment_file
            src = attached.path
            dst = self.get_map_image_path()
            shutil.copyfile(src, default_storage.path(dst))
        else:
            super().prepare_map_image(rooturl)


class PictogramMixin(models.Model):
    pictogram = models.FileField(
        verbose_name=_("Pictogram"),
        upload_to=settings.UPLOAD_DIR,
        max_length=512,
        null=True,
    )

    class Meta:
        abstract = True

    def pictogram_img(self):
        return mark_safe(
            f'<img src="{self.pictogram.url}" class="pictogram_{os.path.splitext(self.pictogram.name)[1][1:]}"/>'
            if self.pictogram
            else "No pictogram"
        )

    pictogram_img.short_description = _("Pictogram")

    def get_pictogram_url(self):
        return self.pictogram.url if self.pictogram else None


class OptionalPictogramMixin(PictogramMixin):
    pictogram = models.FileField(
        verbose_name=_("Pictogram"),
        upload_to=settings.UPLOAD_DIR,
        max_length=512,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class AddPropertyMixin:
    @classmethod
    def add_property(cls, name, func, verbose_name):
        if hasattr(cls, name):
            msg = f"{cls} has already an attribute {name}"
            raise AttributeError(msg)
        setattr(cls, name, property(func))
        setattr(cls, f"{name}_verbose_name", verbose_name)


def get_uuid_duplication(uid_field):
    return uuid.uuid4()


class GeotrekMapEntityMixin(MapEntityMixin):
    elements_duplication = {
        "attachments": {"uuid": get_uuid_duplication},
        "avoid_fields": ["aggregations", "children"],
        "uuid": get_uuid_duplication,
    }

    class Meta:
        abstract = True

    def duplicate(self, **kwargs):
        elements_duplication = self.elements_duplication.copy()
        if "name" in [field.name for field in self._meta.get_fields()]:
            elements_duplication["name"] = f"{self.name} (copy)"
        if "structure" in [field.name for field in self._meta.get_fields()]:
            request = kwargs.pop("request", None)
            if request:
                elements_duplication["structure"] = request.user.profile.structure
        clone = super(MapEntityMixin, self).duplicate(**elements_duplication)
        if hasattr(clone, "mutate"):
            clone.mutate(self)
        return clone
