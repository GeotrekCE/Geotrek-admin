from django.conf import settings
from django.urls import path, register_converter

from mapentity.registry import registry

from geotrek.common.urls import PublishableEntityOptions, LangConverter
from . import models, serializers, views


app_name = 'sensitivity'


class SensitiveAreaEntityOptions(PublishableEntityOptions):
    def get_serializer(self):
        return serializers.SensitiveAreaSerializer

    def get_queryset(self):
        return self.model.objects.existing()


register_converter(LangConverter, 'lang')


urlpatterns = [
    path('api/<lang:lang>/sensitiveareas/<int:pk>.kml',
         views.SensitiveAreaKMLDetail.as_view(), name="sensitivearea_kml_detail"),
    path('api/<lang:lang>/sensitiveareas/<int:pk>/openair',
         views.SensitiveAreaOpenAirDetail.as_view(), name="sensitivearea_openair_detail"),
    path('api/<lang:lang>/sensitiveareas/openair',
         views.SensitiveAreaOpenAirList.as_view(), name="sensitivearea_openair_list"),
]

urlpatterns += registry.register(models.SensitiveArea, SensitiveAreaEntityOptions)
