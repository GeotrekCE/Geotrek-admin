from django.conf import settings
from django.urls import path, include
from rest_framework import routers

from geotrek.api.v2 import views as api_views

router = routers.DefaultRouter()
router.register('structure', api_views.StructureViewSet, basename='structure')
if 'geotrek.core' in settings.INSTALLED_APPS:
    router.register('path', api_views.PathViewSet, basename='path')
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    router.register('trek', api_views.TrekViewSet, basename='trek')
    router.register('poi', api_views.POIViewSet, basename='poi')
    router.register('tour', api_views.TourViewSet, basename='tour')
    router.register('theme', api_views.ThemeViewSet, basename='theme')
    router.register('accessibility', api_views.AccessibilityViewSet, basename='accessibility')
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    router.register('touristiccontent', api_views.TouristicContentViewSet, basename='touristiccontent')
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    router.register('sensitivearea', api_views.SensitiveAreaViewSet, basename='sensitivearea')
    router.register('sportpractice', api_views.SportPracticeViewSet, basename='sportpractice')
if 'geotrek.zoning' in settings.INSTALLED_APPS:
    router.register('city', api_views.CityViewSet, basename='city')
    router.register('district', api_views.DistrictViewSet, basename='district')

app_name = 'apiv2'
urlpatterns = [
    path('', api_views.SwaggerSchemaView.as_view(), name="schema"),
    path('', include(router.urls))
]
