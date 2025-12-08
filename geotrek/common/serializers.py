from django.db import models as django_db_models
from mapentity.serializers import MapentityGeojsonModelSerializer
from rest_framework import serializers as rest_serializers
from rest_framework_gis.fields import GeometrySerializerMethodField

from .models import HDViewPoint


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
