from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from geotrek.api.v2 import views as api_views

router = routers.DefaultRouter()
router.register(r'trek', api_views.TrekViewSet, base_name='trek')
router.register(r'tour', api_views.TourViewSet, base_name='tour')
router.register(r'poi', api_views.POIViewSet, base_name='poi')
router.register(r'path', api_views.PathViewSet, base_name='path')

urlpatterns = [
    url(r'^$', api_views.SwaggerSchemaView.as_view(), name="schema"),
    url(r'^', include(router.urls))
]
