from django.conf.urls import patterns

from .views import (
    PhysicalEdgeLayer, PhysicalEdgeList, PhysicalEdgeDetail, PhysicalEdgeCreate,
    PhysicalEdgeUpdate, PhysicalEdgeDelete, PhysicalEdgeJsonList,
    LandEdgeLayer, LandEdgeList, LandEdgeDetail, LandEdgeCreate,
    LandEdgeUpdate, LandEdgeDelete, LandEdgeJsonList,
    CompetenceEdgeLayer, CompetenceEdgeList, CompetenceEdgeDetail, CompetenceEdgeCreate,
    CompetenceEdgeUpdate, CompetenceEdgeDelete, CompetenceEdgeJsonList,
    WorkManagementEdgeLayer, WorkManagementEdgeList, WorkManagementEdgeDetail, WorkManagementEdgeCreate,
    WorkManagementEdgeUpdate, WorkManagementEdgeDelete, WorkManagementEdgeJsonList,
    SignageManagementEdgeLayer, SignageManagementEdgeList, SignageManagementEdgeDetail, SignageManagementEdgeCreate,
    SignageManagementEdgeUpdate, SignageManagementEdgeDelete, SignageManagementEdgeJsonList,
)

from caminae.mapentity.urlizor import view_classes_to_url


urlpatterns = patterns('', *view_classes_to_url(
    PhysicalEdgeLayer, PhysicalEdgeList, PhysicalEdgeDetail, PhysicalEdgeCreate,
    PhysicalEdgeUpdate, PhysicalEdgeDelete, PhysicalEdgeJsonList,
    LandEdgeLayer, LandEdgeList, LandEdgeDetail, LandEdgeCreate,
    LandEdgeUpdate, LandEdgeDelete, LandEdgeJsonList,
    CompetenceEdgeLayer, CompetenceEdgeList, CompetenceEdgeDetail, CompetenceEdgeCreate,
    CompetenceEdgeUpdate, CompetenceEdgeDelete, CompetenceEdgeJsonList,
    WorkManagementEdgeLayer, WorkManagementEdgeList, WorkManagementEdgeDetail, WorkManagementEdgeCreate,
    WorkManagementEdgeUpdate, WorkManagementEdgeDelete, WorkManagementEdgeJsonList,
    SignageManagementEdgeLayer, SignageManagementEdgeList, SignageManagementEdgeDetail, SignageManagementEdgeCreate,
    SignageManagementEdgeUpdate, SignageManagementEdgeDelete, SignageManagementEdgeJsonList,
))
