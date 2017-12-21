from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter

from geotrek.flatpages.views import FlatPageViewSet, FlatPageMeta


"""
We don't use MapEntity for FlatPages, thus we use Django Rest Framework
without sugar.
"""
router = DefaultRouter(trailing_slash=False)
router.register(r'flatpages', FlatPageViewSet, base_name='flatpages')

urlpatterns = patterns(
    '',
    url(r'^api/(?P<lang>\w+)/', include(router.urls)),
    url(r'^api/(?P<lang>\w\w)/flatpages/(?P<pk>\d+)/meta.html$', FlatPageMeta.as_view(), name="flatpage_meta"),
)
