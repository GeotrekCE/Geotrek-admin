from django.conf import settings
from django.urls import path, re_path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions, routers

from geotrek.api.v2 import views as api_views

router = routers.DefaultRouter()
router.register('structure', api_views.StructureViewSet, basename='structure')
router.register('portal', api_views.TargetPortalViewSet, basename='portal')
router.register('theme', api_views.ThemeViewSet, basename='theme')
router.register('source', api_views.SourceViewSet, basename='source')
router.register('reservationsystem', api_views.ReservationSystemViewSet, basename='reservationsystem')
if 'geotrek.core' in settings.INSTALLED_APPS:
    router.register('path', api_views.PathViewSet, basename='path')
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    router.register('trek', api_views.TrekViewSet, basename='trek')
    router.register('poi', api_views.POIViewSet, basename='poi')
    router.register('poitype', api_views.POITypeViewSet, basename='poitype')
    router.register('tour', api_views.TourViewSet, basename='tour')
    router.register('accessibility', api_views.AccessibilityViewSet, basename='accessibility')
    router.register('route', api_views.RouteViewSet, basename='route')
    router.register('difficulty', api_views.DifficultyViewSet, basename='difficulty')
    router.register('network', api_views.NetworksViewSet, basename='network')
    router.register('practice', api_views.PracticeViewSet, basename='practice')
    router.register('treklabel', api_views.TrekLabelViewSet, basename='treklabel')
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    router.register('touristiccontent', api_views.TouristicContentViewSet, basename='touristiccontent')
    router.register('informationdesk', api_views.InformationDeskViewSet, basename='informationdesk')
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    router.register('sensitivearea', api_views.SensitiveAreaViewSet, basename='sensitivearea')
    router.register('sportpractice', api_views.SportPracticeViewSet, basename='sportpractice')
if 'geotrek.zoning' in settings.INSTALLED_APPS:
    router.register('city', api_views.CityViewSet, basename='city')
    router.register('district', api_views.DistrictViewSet, basename='district')


schema_view = get_schema_view(
    openapi.Info(
        title="Geotrek API v2",
        default_version='v2',
        description="New Geotrek API.",
    ),
    urlconf='geotrek.api.v2.urls',
    public=True,
    permission_classes=(permissions.AllowAny,),
)

app_name = 'apiv2'
urlpatterns = [
    re_path(r'^api/v2.json$', schema_view.without_ui(cache_timeout=0), {'format': '.json'}, name='schema-json'),
    re_path(r'^api/v2/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^api/v2/doc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/v2/config/', api_views.ConfigView.as_view(), name='config'),
    path('api/v2/', include(router.urls)),
]
