from django.conf.urls import patterns, url

# from .views import PathList, path_list, path_create_or_edit
from .views import PathList, path_list
from .views import PathDetail, PathCreate, PathUpdate, PathDelete


urlpatterns = patterns('',
    url(r'^path.geojson$', PathList.as_view(), name="layerpath"),

    url(r'^path/list/$', path_list, name="path_list"),
    # url(r'^path/add/$', path_create_or_edit, name="path_add"),
    # url(r'^path/edit/(?P<path_id>\d+)/$', path_create_or_edit, name="path_edit"),

    url(r'path/(?P<pk>\d+)/$', PathDetail.as_view(), name='path_detail'),
    url(r'path/add/$', PathCreate.as_view(), name='path_add'),
    url(r'path/edit/(?P<pk>\d+)/$', PathUpdate.as_view(), name='path_update'),
    url(r'path/(?P<pk>\d+)/delete/$', PathDelete.as_view(), name='path_delete'),
)
