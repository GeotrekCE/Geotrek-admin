from django.conf import settings
from django.urls import path, include
from rest_framework import routers

from geotrek.api.v2 import views as api_views

router = routers.DefaultRouter()
router.register('structure', api_views.StructureViewSet, base_name='structure')
if 'geotrek.core' in settings.INSTALLED_APPS:
    router.register('path', api_views.PathViewSet, base_name='path')
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    router.register('trek', api_views.TrekViewSet, base_name='trek')
    router.register('poi', api_views.POIViewSet, base_name='poi')
    router.register('tour', api_views.TourViewSet, base_name='tour')
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    router.register('touristiccontent', api_views.TouristicContentViewSet, base_name='touristiccontent')
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    router.register('sensitivearea', api_views.SensitiveAreaViewSet, base_name='sensitivearea')
    router.register('sportpractice', api_views.SportPracticeViewSet, base_name='sportpractice')

app_name = 'apiv2'
urlpatterns = [
    path('', api_views.SwaggerSchemaView.as_view(), name="schema"),
    path('', include(router.urls))
]
