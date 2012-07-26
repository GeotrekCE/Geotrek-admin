from django.conf.urls import patterns, url

from caminae.authent.decorators import path_manager_required

from .views import (PathLayer, PathList, PathDetail, PathCreate, 
                    PathUpdate, PathDelete)


urlpatterns = patterns('',
    url(r'^path.geojson$', PathLayer.as_view(), name="layer_path"),
)

urlpatterns += patterns('',
    url(r'^path/list/$', PathList, name="path_list"),
    url(r'^path/(?P<pk>\d+)/$', PathDetail.as_view(), name='path_detail'),
    url(r'^path/add/$', path_manager_required('core:path_list')(PathCreate.as_view()), name='path_add'),
    url(r'^path/edit/(?P<pk>\d+)/$', path_manager_required('core:path_detail')(PathUpdate.as_view()), name='path_update'),
    url(r'^path//delete/(?P<pk>\d+)$', path_manager_required('core:path_detail')(PathDelete.as_view()), name='path_delete'),
)
