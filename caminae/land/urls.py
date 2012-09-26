from django.conf.urls import patterns

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
