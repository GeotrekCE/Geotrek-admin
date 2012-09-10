from django.conf.urls import patterns

from .views import (
    PhysicalEdgeLayer, PhysicalEdgeList, PhysicalEdgeDetail, PhysicalEdgeCreate,
    PhysicalEdgeUpdate, PhysicalEdgeDelete, PhysicalEdgeJsonList, PhysicalEdgeFormatList,
    LandEdgeLayer, LandEdgeList, LandEdgeDetail, LandEdgeCreate,
    LandEdgeUpdate, LandEdgeDelete, LandEdgeJsonList, LandEdgeFormatList,
    CompetenceEdgeLayer, CompetenceEdgeList, CompetenceEdgeDetail, CompetenceEdgeCreate,
    CompetenceEdgeUpdate, CompetenceEdgeDelete, CompetenceEdgeJsonList, CompetenceEdgeFormatList,
    WorkManagementEdgeLayer, WorkManagementEdgeList, WorkManagementEdgeDetail, WorkManagementEdgeCreate,
    WorkManagementEdgeUpdate, WorkManagementEdgeDelete, WorkManagementEdgeJsonList, WorkManagementEdgeFormatList,
    SignageManagementEdgeLayer, SignageManagementEdgeList, SignageManagementEdgeDetail, SignageManagementEdgeCreate,
    SignageManagementEdgeUpdate, SignageManagementEdgeDelete, SignageManagementEdgeJsonList, SignageManagementEdgeFormatList,
)

from caminae.mapentity.urlizor import view_classes_to_url


urlpatterns = patterns('', *view_classes_to_url(
    PhysicalEdgeLayer, PhysicalEdgeList, PhysicalEdgeDetail, PhysicalEdgeCreate,
    PhysicalEdgeUpdate, PhysicalEdgeDelete, PhysicalEdgeJsonList, PhysicalEdgeFormatList,
    LandEdgeLayer, LandEdgeList, LandEdgeDetail, LandEdgeCreate,
    LandEdgeUpdate, LandEdgeDelete, LandEdgeJsonList, LandEdgeFormatList,
    CompetenceEdgeLayer, CompetenceEdgeList, CompetenceEdgeDetail, CompetenceEdgeCreate,
    CompetenceEdgeUpdate, CompetenceEdgeDelete, CompetenceEdgeJsonList, CompetenceEdgeFormatList,
    WorkManagementEdgeLayer, WorkManagementEdgeList, WorkManagementEdgeDetail, WorkManagementEdgeCreate,
    WorkManagementEdgeUpdate, WorkManagementEdgeDelete, WorkManagementEdgeJsonList, WorkManagementEdgeFormatList,
    SignageManagementEdgeLayer, SignageManagementEdgeList, SignageManagementEdgeDetail, SignageManagementEdgeCreate,
    SignageManagementEdgeUpdate, SignageManagementEdgeDelete, SignageManagementEdgeJsonList, SignageManagementEdgeFormatList,
))

