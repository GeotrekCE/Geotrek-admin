from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter

from geotrek.flatpages.views import FlatPageViewSet


"""
We don't use MapEntity for FlatPages, thus we use Django Rest Framework
without sugar.
"""
router = DefaultRouter()
router.register(r'flatpages', FlatPageViewSet)

urlpatterns = patterns('',
    url(r'^api/', include(router.urls)),
)
