import mimetypes
import os
from io import BytesIO

import magic
from django.conf import settings
from django.db import models as django_db_models
from django.utils.translation import gettext_lazy as _
from mapentity.serializers import MapentityGeojsonModelSerializer
from PIL import Image, UnidentifiedImageError
from rest_framework import serializers as rest_serializers
from rest_framework_gis.fields import GeometrySerializerMethodField

from ..authent.models import Structure
from .models import AccessMean, Attachment, FileType, HDViewPoint, License, Organism


class TranslatedModelSerializer(rest_serializers.ModelSerializer):
    def get_field(self, model_field):
        kwargs = {}
        if issubclass(
            model_field.__class__,
            django_db_models.CharField | django_db_models.TextField,
        ):
            if model_field.null:
                kwargs["allow_none"] = True
            kwargs["max_length"] = getattr(model_field, "max_length")
            return rest_serializers.CharField(**kwargs)
        return super().get_field(model_field)


class PictogramSerializerMixin(rest_serializers.ModelSerializer):
    pictogram = rest_serializers.ReadOnlyField(source="get_pictogram_url")


class PicturesSerializerMixin(rest_serializers.ModelSerializer):
    thumbnail = rest_serializers.ReadOnlyField(source="serializable_thumbnail")
    pictures = rest_serializers.ReadOnlyField(source="serializable_pictures")
    videos = rest_serializers.ReadOnlyField(source="serializable_videos")
    files = rest_serializers.ReadOnlyField(source="serializable_files")

    class Meta:
        fields = ("thumbnail", "pictures", "videos", "files")


class BasePublishableSerializerMixin(rest_serializers.ModelSerializer):
    class Meta:
        fields = ("published", "published_status", "publication_date")


class HDViewPointSerializer(TranslatedModelSerializer):
    class Meta:
        model = HDViewPoint
        fields = ("id", "uuid", "author", "title", "legend", "license")


class HDViewPointGeoJSONSerializer(MapentityGeojsonModelSerializer):
    api_geom = GeometrySerializerMethodField()

    def get_api_geom(self, obj):
        return obj.geom.transform(4326, clone=True)

    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = HDViewPoint
        fields = ("id", "title")


class HDViewPointAPISerializer(HDViewPointSerializer):
    class Meta(HDViewPointSerializer.Meta):
        id_field = "id"
        fields = HDViewPointSerializer.Meta.fields


class FileTypeSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = FileType
        fields = ("id", "type")


class LicenseSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = License
        fields = ("id", "label")


class AttachmentSerializer(rest_serializers.ModelSerializer):
    attachment_file = rest_serializers.FileField(required=True)

    class Meta:
        model = Attachment
        fields = [
            "id",
            "content_type",
            "object_id",
            "attachment_file",
            "filetype",
            "license",
            "author",
            "title",
            "legend",
            "creator",
        ]

    def validate_attachment_file(self, file):
        """
        Check that file extensions and mimetypes are allowed
        """

        # Check file size
        if (
            settings.PAPERCLIP_MAX_BYTES_SIZE_IMAGE
            and settings.PAPERCLIP_MAX_BYTES_SIZE_IMAGE < file.size
        ):
            msg = _("The uploaded file is too large")
            raise rest_serializers.ValidationError(msg)

        # Check extension and mimetype
        if settings.PAPERCLIP_ALLOWED_EXTENSIONS is not None:
            extension = os.path.splitext(file.name)[1].lstrip(".").lower()
            if extension not in settings.PAPERCLIP_ALLOWED_EXTENSIONS:
                msg = _("File type '%(ext)s' not allowed") % {"ext": extension}
                raise rest_serializers.ValidationError(msg)

            file.seek(0)
            file_mimetype = magic.from_buffer(file.read(), mime=True)
            file.seek(0)

            file_mimetype_allowed = f".{extension}" in mimetypes.guess_all_extensions(
                file_mimetype
            )
            file_mimetype_allowed = file_mimetype_allowed or (
                settings.PAPERCLIP_EXTRA_ALLOWED_MIMETYPES.get(extension, False)
                and file_mimetype
                in settings.PAPERCLIP_EXTRA_ALLOWED_MIMETYPES.get(extension)
            )
            if not file_mimetype_allowed:
                msg = _("File mime type '%(mimetype)s' is not allowed for %(ext)s.") % {
                    "mimetype": file_mimetype,
                    "ext": extension,
                }
                raise rest_serializers.ValidationError(msg)

        # Check image dimensions
        try:
            image = Image.open(BytesIO(file.read()))
            if (
                settings.PAPERCLIP_MIN_IMAGE_UPLOAD_WIDTH
                and settings.PAPERCLIP_MIN_IMAGE_UPLOAD_WIDTH > image.width
            ):
                msg = _("The uploaded file is not wide enough")
                raise rest_serializers.ValidationError(msg)
            if (
                settings.PAPERCLIP_MIN_IMAGE_UPLOAD_HEIGHT
                and settings.PAPERCLIP_MIN_IMAGE_UPLOAD_HEIGHT > image.height
            ):
                msg = _("The uploaded file is not tall enough")
                raise rest_serializers.ValidationError(msg)
        except UnidentifiedImageError:
            pass
        except ValueError:
            msg = _("Decompressed Data Too Large")
            raise rest_serializers.ValidationError(msg)
        finally:
            file.seek(0)

        return file


class StructureGTAMSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = Structure
        fields = ("id", "name")


class OrganismGTAMSerializer(rest_serializers.ModelSerializer):
    name = rest_serializers.CharField(source="organism")

    class Meta:
        model = Organism
        fields = ("id", "name")


class AccessMeanGTAMSerializer(rest_serializers.ModelSerializer):
    name = rest_serializers.CharField(source="label")

    class Meta:
        model = AccessMean
        fields = ("id", "name")
