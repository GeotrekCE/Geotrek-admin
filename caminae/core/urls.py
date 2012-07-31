from django.conf.urls import patterns, url

from .views import (PathLayer, PathList, PathDetail, PathCreate, 
                    PathUpdate, PathDelete, PathAjaxList)


urlpatterns = patterns('',
    url(r'^data/paths.geojson$', PathLayer.as_view(), name="layer_path"),
)

urlpatterns += patterns('',
    url(r'^path/list/$', PathList.as_view(), name="path_list"),
    url(r'^path/(?P<pk>\d+)/$', PathDetail.as_view(), name='path_detail'),
    url(r'^path/add/$', PathCreate.as_view(), name='path_add'),
    url(r'^path/edit/(?P<pk>\d+)/$', PathUpdate.as_view(), name='path_update'),
    url(r'^path/delete/(?P<pk>\d+)$', PathDelete.as_view(), name='path_delete'),

    url(r'^path/ajax_list/$', PathAjaxList.as_view(), name="path_ajax_list"),
)
