from django.conf.urls import patterns, url

from .views import (
    PhysicalEdgeLayer, PhysicalEdgeList, PhysicalEdgeDetail, PhysicalEdgeDocument, PhysicalEdgeCreate,
    PhysicalEdgeUpdate, PhysicalEdgeDelete, PhysicalEdgeJsonList, PhysicalEdgeFormatList,
    LandEdgeLayer, LandEdgeList, LandEdgeDetail, LandEdgeDocument, LandEdgeCreate,
    LandEdgeUpdate, LandEdgeDelete, LandEdgeJsonList, LandEdgeFormatList,
    CompetenceEdgeLayer, CompetenceEdgeList, CompetenceEdgeDetail, CompetenceEdgeDocument, CompetenceEdgeCreate,
    CompetenceEdgeUpdate, CompetenceEdgeDelete, CompetenceEdgeJsonList, CompetenceEdgeFormatList,
    WorkManagementEdgeLayer, WorkManagementEdgeList, WorkManagementEdgeDetail, WorkManagementEdgeDocument, WorkManagementEdgeCreate,
    WorkManagementEdgeUpdate, WorkManagementEdgeDelete, WorkManagementEdgeJsonList, WorkManagementEdgeFormatList,
    SignageManagementEdgeLayer, SignageManagementEdgeList, SignageManagementEdgeDetail, SignageManagementEdgeDocument, SignageManagementEdgeCreate,
    SignageManagementEdgeUpdate, SignageManagementEdgeDelete, SignageManagementEdgeJsonList, SignageManagementEdgeFormatList,
    
    CityGeoJSONLayer, RestrictedAreaGeoJSONLayer, DistrictGeoJSONLayer
)

from caminae.mapentity.urlizor import view_classes_to_url


urlpatterns = patterns('',
    url(r'^api/city/city.geojson$', CityGeoJSONLayer.as_view(), name="city_layer"), 
    url(r'^api/restrictedarea/restrictedarea.geojson$', RestrictedAreaGeoJSONLayer.as_view(), name="restrictedarea_layer"), 
    url(r'^api/district/district.geojson$', DistrictGeoJSONLayer.as_view(), name="district_layer"), 
    
    *view_classes_to_url(
        PhysicalEdgeLayer, PhysicalEdgeList, PhysicalEdgeDetail, PhysicalEdgeDocument, PhysicalEdgeCreate,
        PhysicalEdgeUpdate, PhysicalEdgeDelete, PhysicalEdgeJsonList, PhysicalEdgeFormatList,
        LandEdgeLayer, LandEdgeList, LandEdgeDetail, LandEdgeDocument, LandEdgeCreate,
        LandEdgeUpdate, LandEdgeDelete, LandEdgeJsonList, LandEdgeFormatList,
        CompetenceEdgeLayer, CompetenceEdgeList, CompetenceEdgeDetail, CompetenceEdgeDocument, CompetenceEdgeCreate,
        CompetenceEdgeUpdate, CompetenceEdgeDelete, CompetenceEdgeJsonList, CompetenceEdgeFormatList,
        WorkManagementEdgeLayer, WorkManagementEdgeList, WorkManagementEdgeDetail, WorkManagementEdgeDocument, WorkManagementEdgeCreate,
        WorkManagementEdgeUpdate, WorkManagementEdgeDelete, WorkManagementEdgeJsonList, WorkManagementEdgeFormatList,
        SignageManagementEdgeLayer, SignageManagementEdgeList, SignageManagementEdgeDetail, SignageManagementEdgeDocument, SignageManagementEdgeCreate,
        SignageManagementEdgeUpdate, SignageManagementEdgeDelete, SignageManagementEdgeJsonList, SignageManagementEdgeFormatList,
    )
)
