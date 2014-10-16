from django.core.urlresolvers import reverse
from django.db import models as django_db_models

from rest_framework import serializers as rest_serializers
from rest_framework import serializers as rest_fields


class TranslatedModelSerializer(rest_serializers.ModelSerializer):
    def get_field(self, model_field):
        kwargs = {}
        if issubclass(model_field.__class__,
                      (django_db_models.CharField,
                       django_db_models.TextField)):
            if model_field.null:
                kwargs['allow_none'] = True
            kwargs['max_length'] = getattr(model_field, 'max_length')
            return rest_fields.CharField(**kwargs)
        return super(TranslatedModelSerializer, self).get_field(model_field)


class PictogramSerializerMixin(rest_serializers.ModelSerializer):
    pictogram = rest_serializers.Field('get_pictogram_url')


class PicturesSerializerMixin(rest_serializers.ModelSerializer):
    thumbnail = rest_serializers.Field(source='serializable_thumbnail')
    pictures = rest_serializers.Field(source='serializable_pictures')

    class Meta:
        fields = ('thumbnail', 'pictures',)


class PublishableSerializerMixin(rest_serializers.ModelSerializer):
    slug = rest_serializers.Field(source='slug')
    published_status = rest_serializers.Field(source='published_status')

    map_image_url = rest_serializers.Field(source='map_image_url')
    printable = rest_serializers.SerializerMethodField('get_printable_url')
    filelist_url = rest_serializers.SerializerMethodField('get_filelist_url')

    def get_printable_url(self, obj):
        appname = obj._meta.app_label
        modelname = obj._meta.module_name
        return reverse('%s:%s_printable' % (appname, modelname),
                       kwargs={'pk': obj.pk})

    def get_filelist_url(self, obj):
        appname = obj._meta.app_label
        modelname = obj._meta.module_name
        return reverse('get_attachments', kwargs={'app_label': appname,
                                                  'module_name': modelname,
                                                  'pk': obj.pk})

    class Meta:
        fields = ('name', 'slug', 'published', 'published_status', 'publication_date',
                  'map_image_url', 'filelist_url', 'printable')
