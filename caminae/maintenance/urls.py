from django.conf.urls import patterns, url

from .views import (
    InterventionLayer, InterventionList, InterventionDetail, InterventionCreate,
    InterventionUpdate, InterventionDelete, InterventionJsonList
)


urlpatterns = patterns('',
    url(r'^data/interventions.geojson$', InterventionLayer.as_view(), name="intervention_layer"),
    url(r'^data/interventions.json$', InterventionJsonList.as_view(), name="intervention_json_list"),
)

urlpatterns += patterns('',
    url(r'^intervention/list/$', InterventionList.as_view(), name="intervention_list"),
    url(r'^intervention/add/$', InterventionCreate.as_view(), name='intervention_add'),
    url(r'^intervention/(?P<pk>\d+)/$', InterventionDetail.as_view(), name='intervention_detail'),
    url(r'^intervention/edit/(?P<pk>\d+)/$', InterventionUpdate.as_view(), name='intervention_update'),
    url(r'^intervention/delete/(?P<pk>\d+)$', InterventionDelete.as_view(), name='intervention_delete'),
)
