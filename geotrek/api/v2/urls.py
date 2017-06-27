from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from geotrek.api.v2 import views as api_views

router = routers.DefaultRouter()
router.register(r'touristiccontent', api_views.TouristicContentViewSet)
router.register(r'trek', api_views.TrekViewSet, base_name='trek')
router.register(r'roaming', api_views.RoamingViewSet, base_name='roaming')
router.register(r'poi', api_views.POIViewSet, base_name='poi')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework'))
]

# urlpatterns += router.urls
