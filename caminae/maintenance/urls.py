from django.conf.urls import patterns, url

from .views import (
    InterventionLayer, InterventionList, InterventionDetail, InterventionCreate,
    InterventionUpdate, InterventionDelete, InterventionJsonList
)

from caminae.mapentity.urlizor import view_classes_to_url


urlpatterns = patterns('', *view_classes_to_url(
    InterventionLayer, InterventionList, InterventionDetail, InterventionCreate,
    InterventionUpdate, InterventionDelete, InterventionJsonList
))

