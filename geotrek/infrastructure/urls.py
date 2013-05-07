from django.conf.urls import patterns

from .views import (
    InfrastructureLayer, InfrastructureList, InfrastructureDetail, InfrastructureDocument, InfrastructureCreate,
    InfrastructureUpdate, InfrastructureDelete, InfrastructureJsonList, InfrastructureFormatList,
    SignageLayer, SignageList, SignageDetail, SignageDocument, SignageCreate,
    SignageUpdate, SignageDelete, SignageJsonList, SignageFormatList,
)

from mapentity.urlizor import view_classes_to_url


urlpatterns = patterns('', *view_classes_to_url(
    InfrastructureLayer, InfrastructureList, InfrastructureDetail, InfrastructureDocument, InfrastructureCreate,
    InfrastructureUpdate, InfrastructureDelete, InfrastructureJsonList, InfrastructureFormatList,
    SignageLayer, SignageList, SignageDetail, SignageDocument, SignageCreate,
    SignageUpdate, SignageDelete, SignageJsonList, SignageFormatList,
))
