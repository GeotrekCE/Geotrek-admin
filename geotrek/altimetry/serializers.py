from rest_framework import serializers as rest_serializers
from django.core.urlresolvers import reverse
from django.utils.translation import get_language

from geotrek.core.models import AltimetryMixin


class AltimetrySerializerMixin(rest_serializers.ModelSerializer):
    elevation_area_url = rest_serializers.SerializerMethodField()
    elevation_svg_url = rest_serializers.SerializerMethodField()
    altimetric_profile = rest_serializers.SerializerMethodField('get_altimetric_profile_url')

    class Meta:
        fields = ('elevation_area_url', 'elevation_svg_url', 'altimetric_profile') + (
            tuple(AltimetryMixin.COLUMNS))

    def get_elevation_area_url(self, obj):
        appname = obj._meta.app_label
        modelname = obj._meta.model_name
        return reverse('%s:%s_elevation_area' % (appname, modelname), kwargs={'lang': get_language(), 'pk': obj.pk})

    def get_elevation_svg_url(self, obj):
        appname = obj._meta.app_label
        modelname = obj._meta.model_name
        return reverse('%s:%s_profile_svg' % (appname, modelname), kwargs={'lang': get_language(), 'pk': obj.pk})

    def get_altimetric_profile_url(self, obj):
        appname = obj._meta.app_label
        modelname = obj._meta.model_name
        return reverse('%s:%s_profile' % (appname, modelname), kwargs={'lang': get_language(), 'pk': obj.pk})
