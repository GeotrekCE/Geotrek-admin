from django.conf import settings
from django.conf.urls import url, include
from rest_framework import routers

from geotrek.api.v2 import views as api_views

router = routers.DefaultRouter()
router.register(r'structure', api_views.StructureViewSet, base_name='structure')
if 'geotrek.core' in settings.INSTALLED_APPS:
    router.register(r'path', api_views.PathViewSet, base_name='path')
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    router.register(r'trek', api_views.TrekViewSet, base_name='trek')
    router.register(r'poi', api_views.POIViewSet, base_name='poi')
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    router.register(r'tour', api_views.TourViewSet, base_name='tour')
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    router.register(r'sensitivearea', api_views.SensitiveAreaViewSet, base_name='sensitivearea')
    router.register(r'sportpractice', api_views.SportPracticeViewSet, base_name='sportpractice')

urlpatterns = [
    url(r'^$', api_views.SwaggerSchemaView.as_view(), name="schema"),
    url(r'^', include(router.urls))
]
