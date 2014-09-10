from rest_framework import serializers as rest_serializers
from django.core.urlresolvers import reverse

from geotrek.core.models import AltimetryMixin


class AltimetrySerializerMixin(rest_serializers.ModelSerializer):
    elevation_area_url = rest_serializers.SerializerMethodField('get_elevation_area_url')
    altimetric_profile = rest_serializers.SerializerMethodField('get_altimetric_profile_url')

    class Meta:
        fields = ('elevation_area_url', 'altimetric_profile') + \
                 tuple(AltimetryMixin.COLUMNS)

    def get_elevation_area_url(self, obj):
        return reverse('trekking:trek_elevation_area', kwargs={'pk': obj.pk})

    def get_altimetric_profile_url(self, obj):
        return reverse('trekking:trek_profile', kwargs={'pk': obj.pk})
