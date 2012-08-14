from django.conf.urls import patterns

from .views import (
    InfrastructureLayer, InfrastructureList, InfrastructureDetail, InfrastructureCreate,
    InfrastructureUpdate, InfrastructureDelete, InfrastructureJsonList,
    SignageLayer, SignageList, SignageDetail, SignageCreate,
    SignageUpdate, SignageDelete, SignageJsonList,
)

from caminae.mapentity.urlizor import view_classes_to_url


urlpatterns = patterns('', *view_classes_to_url(
    InfrastructureLayer, InfrastructureList, InfrastructureDetail, InfrastructureCreate,
    InfrastructureUpdate, InfrastructureDelete, InfrastructureJsonList,
    SignageLayer, SignageList, SignageDetail, SignageCreate,
    SignageUpdate, SignageDelete, SignageJsonList,
))
