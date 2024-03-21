from django.urls import path, register_converter

from mapentity.registry import registry

from geotrek.common.urls import PublishableEntityOptions, LangConverter
from . import models, views


app_name = 'sensitivity'


register_converter(LangConverter, 'lang')


urlpatterns = [
    path('api/<lang:lang>/sensitiveareas/<int:pk>.kml',
         views.SensitiveAreaKMLDetail.as_view(), name="sensitivearea_kml_detail"),
    path('api/<lang:lang>/sensitiveareas/<int:pk>/openair',
         views.SensitiveAreaOpenAirDetail.as_view(), name="sensitivearea_openair_detail"),
    path('api/<lang:lang>/sensitiveareas/openair',
         views.SensitiveAreaOpenAirList.as_view(), name="sensitivearea_openair_list"),
]

urlpatterns += registry.register(models.SensitiveArea, PublishableEntityOptions)
