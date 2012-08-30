from django.conf.urls.defaults import *
from .views import add_attachment, delete_attachment, ajax_validate_attachment

urlpatterns = patterns('',
    url(r'^add-for/(?P<app_label>[\w\-]+)/(?P<module_name>[\w\-]+)/(?P<pk>\d+)/$', add_attachment, name="add_attachment"),
    url(r'^delete/(?P<attachment_pk>\d+)/$', delete_attachment, name="delete_attachment"),
    url(r'^ajax_validate/$', ajax_validate_attachment, name="ajax_validate_attachment"),
)
