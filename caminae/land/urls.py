from django.conf.urls import patterns, url

from .views import (
    CityLayer, DistrictLayer,
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

from caminae.mapentity.urlizor import view_classes_to_url


urlpatterns = patterns('', *view_classes_to_url(
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
))

urlpatterns += patterns('',
    url(r'api/city/city.geojson', CityLayer.as_view(), name='city_layer'),
    url(r'api/district/district.geojson', DistrictLayer.as_view(), name='district_layer'),
)

