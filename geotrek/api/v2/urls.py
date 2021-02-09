from django.conf import settings
from django.urls import path, include
from rest_framework import routers

from geotrek.api.v2 import views as api_views


router = routers.DefaultRouter()
router.register('structure', api_views.StructureViewSet, basename='structure')
router.register('portal', api_views.TargetPortalViewSet, basename='portal')
router.register('theme', api_views.ThemeViewSet, basename='theme')
router.register('source', api_views.SourceViewSet, basename='source')
router.register('reservationsystem', api_views.ReservationSystemViewSet, basename='reservationsystem')
router.register('label', api_views.LabelViewSet, basename='label')
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
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    router.register('touristiccontentcategory', api_views.TouristicContentCategoryViewSet,
                    basename='touristiccontentcategory')
    router.register('touristiccontent', api_views.TouristicContentViewSet, basename='touristiccontent')
    router.register('informationdesk', api_views.InformationDeskViewSet, basename='informationdesk')
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    router.register('sensitivearea', api_views.SensitiveAreaViewSet, basename='sensitivearea')
    router.register('sportpractice', api_views.SportPracticeViewSet, basename='sportpractice')
if 'geotrek.zoning' in settings.INSTALLED_APPS:
    router.register('city', api_views.CityViewSet, basename='city')
    router.register('district', api_views.DistrictViewSet, basename='district')
if 'geotrek.outdoor' in settings.INSTALLED_APPS:
    router.register('site', api_views.SiteViewSet, basename='site')
    router.register('outdoorpractice', api_views.OutdoorPracticeViewSet, basename='outdoor-practice')
    router.register('sitetype', api_views.SiteTypeViewSet, basename='sitetype')
    router.register('ratingscale', api_views.RatingScaleViewSet, basename='ratingscale')
    router.register('rating', api_views.RatingViewSet, basename='rating')
if 'geotrek.flatpages' in settings.INSTALLED_APPS:
    router.register('flatpage', api_views.FlatPageViewSet, basename='flatpage')

app_name = 'apiv2'
_urlpatterns = []
if 'drf_yasg' in settings.INSTALLED_APPS:
    _urlpatterns.append(path('', api_views.schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'))
_urlpatterns += [
    path('config/', api_views.ConfigView.as_view(), name='config'),
    path('', include(router.urls)),
]
urlpatterns = [path('api/v2/', include(_urlpatterns))]
