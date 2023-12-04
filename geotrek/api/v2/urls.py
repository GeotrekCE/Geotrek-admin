from django.conf import settings
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework import routers

from geotrek.api.v2 import views as api_views


router = routers.DefaultRouter()
router.register('structure', api_views.StructureViewSet, basename='structure')
router.register('portal', api_views.TargetPortalViewSet, basename='portal')
router.register('theme', api_views.ThemeViewSet, basename='theme')
router.register('source', api_views.SourceViewSet, basename='source')
router.register('reservationsystem', api_views.ReservationSystemViewSet, basename='reservationsystem')
router.register('label', api_views.LabelViewSet, basename='label')
router.register('organism', api_views.OrganismViewSet, basename='organism')
router.register('file_type', api_views.FileTypeViewSet, basename='filetype')
if 'geotrek.core' in settings.INSTALLED_APPS:
    router.register('path', api_views.PathViewSet, basename='path')
if 'geotrek.infrastructure' in settings.INSTALLED_APPS:
    router.register('infrastructure', api_views.InfrastructureViewSet, basename='infrastructure')
    router.register('infrastructure_type', api_views.InfrastructureTypeViewSet, basename='infrastructure-type')
    router.register('infrastructure_condition', api_views.InfrastructureConditionViewSet, basename='infrastructure-condition')
    router.register('infrastructure_usage_difficulty_level', api_views.InfrastructureUsageDifficultyLevelViewSet, basename='infrastructure-usage-difficulty')
    router.register('infrastructure_maintenance_difficulty_level', api_views.InfrastructureMaintenanceDifficultyLevelViewSet, basename='infrastructure-maintenance-difficulty')
if 'geotrek.feedback' in settings.INSTALLED_APPS:
    router.register('feedback_status', api_views.ReportStatusViewSet, basename='feedback-status')
    router.register('feedback_category', api_views.ReportCategoryViewSet, basename='feedback-category')
    router.register('feedback_activity', api_views.ReportActivityViewSet, basename='feedback-activity')
    router.register('feedback_magnitude', api_views.ReportProblemMagnitudeViewSet, basename='feedback-magnitude')
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    router.register('trek', api_views.TrekViewSet, basename='trek')
    router.register('poi', api_views.POIViewSet, basename='poi')
    router.register('poi_type', api_views.POITypeViewSet, basename='poitype')
    router.register('tour', api_views.TourViewSet, basename='tour')
    router.register('trek_accessibility', api_views.AccessibilityViewSet, basename='accessibility')
    router.register('trek_accessibility_level', api_views.AccessibilityLevelViewSet, basename='accessibility-level')
    router.register('trek_route', api_views.RouteViewSet, basename='route')
    router.register('trek_difficulty', api_views.DifficultyViewSet, basename='difficulty')
    router.register('trek_network', api_views.NetworkViewSet, basename='network')
    router.register('trek_practice', api_views.PracticeViewSet, basename='practice')
    router.register('trek_ratingscale', api_views.TrekRatingScaleViewSet, basename='trek-ratingscale')
    router.register('trek_rating', api_views.TrekRatingViewSet, basename='trek-rating')
    router.register('weblink_category', api_views.WebLinkCategoryViewSet, basename='weblink-category')
    router.register('service_type', api_views.ServiceTypeViewSet, basename='servicetype')
    router.register('service', api_views.ServiceViewSet, basename='service')
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    router.register('touristiccontent_category', api_views.TouristicContentCategoryViewSet,
                    basename='touristiccontentcategory')
    router.register('touristiccontent', api_views.TouristicContentViewSet, basename='touristiccontent')
    router.register('touristicevent', api_views.TouristicEventViewSet, basename='touristicevent')
    router.register('touristicevent_type', api_views.TouristicEventTypeViewSet, basename='touristiceventtype')
    router.register('touristicevent_place', api_views.TouristicEventPlaceViewSet, basename='touristiceventplace')
    router.register('touristicevent_organizer', api_views.TouristicEventOrganizerViewSet, basename='touristiceventorganizer')
    router.register('informationdesk', api_views.InformationDeskViewSet, basename='informationdesk')
    router.register('informationdesk_type', api_views.InformationDeskTypeViewSet, basename='informationdesktype')
    router.register('label_accessibility', api_views.LabelAccessibilityViewSet, basename='labelaccessibility')
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    router.register('sensitivearea', api_views.SensitiveAreaViewSet, basename='sensitivearea')
    router.register('sensitivearea_practice', api_views.SportPracticeViewSet, basename='sportpractice')
    router.register('sensitivearea_species', api_views.SpeciesViewSet, basename='species')
if 'geotrek.zoning' in settings.INSTALLED_APPS:
    router.register('city', api_views.CityViewSet, basename='city')
    router.register('district', api_views.DistrictViewSet, basename='district')
if 'geotrek.outdoor' in settings.INSTALLED_APPS:
    router.register('outdoor_site', api_views.SiteViewSet, basename='site')
    router.register('outdoor_practice', api_views.OutdoorPracticeViewSet, basename='outdoor-practice')
    router.register('outdoor_sector', api_views.SectorViewSet, basename='outdoor-sector')
    router.register('outdoor_sitetype', api_views.SiteTypeViewSet, basename='sitetype')
    router.register('outdoor_coursetype', api_views.CourseTypeViewSet, basename='coursetype')
    router.register('outdoor_ratingscale', api_views.OutdoorRatingScaleViewSet, basename='outdoor-ratingscale')
    router.register('outdoor_rating', api_views.OutdoorRatingViewSet, basename='outdoor-rating')
    router.register('outdoor_course', api_views.CourseViewSet, basename='course')
if 'geotrek.flatpages' in settings.INSTALLED_APPS:
    router.register('flatpage', api_views.FlatPageViewSet, basename='flatpage')
if 'geotrek.signage' in settings.INSTALLED_APPS:
    router.register('signage', api_views.SignageViewSet, basename='signage')
    router.register('signage_type', api_views.SignageTypeViewSet, basename='signage-type')
    router.register('signage_blade_type', api_views.BladeTypeViewSet, basename='signage-blade-type')
    router.register('signage_sealing', api_views.SealingViewSet, basename='signage-sealing')
    router.register('signage_color', api_views.ColorViewSet, basename='signage-color')
    router.register('signage_direction', api_views.DirectionViewSet, basename='signage-direction')
    router.register('hdviewpoint', api_views.HDViewPointViewSet, basename='hdviewpoint')


app_name = 'apiv2'
_urlpatterns = []
if 'drf_yasg' in settings.INSTALLED_APPS:
    _urlpatterns.append(path('', api_views.schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'))
_urlpatterns += [
    path('config/', api_views.ConfigView.as_view(), name='config'),
    path('sportpractice/', RedirectView.as_view(pattern_name='apiv2:sportpractice-list', permanent=True)),
    path('sportpractice/<int:pk>/', RedirectView.as_view(pattern_name='apiv2:sportpractice-detail', permanent=True)),
    path('version', api_views.GeotrekVersionAPIView.as_view()),
    path('', include(router.urls)),
]
urlpatterns = [path('api/v2/', include(_urlpatterns))]
