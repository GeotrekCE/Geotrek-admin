from django.conf.urls import patterns, url

from mapentity.urlizor import view_classes_to_url

from . import views


urlpatterns = patterns('',
    url(r'^api/city/city.geojson$', views.CityGeoJSONLayer.as_view(), name="city_layer"), 
    url(r'^api/restrictedarea/restrictedarea.geojson$', views.RestrictedAreaGeoJSONLayer.as_view(), name="restrictedarea_layer"), 
    url(r'^api/district/district.geojson$', views.DistrictGeoJSONLayer.as_view(), name="district_layer"), 
    
    *view_classes_to_url(
        views.PhysicalEdgeLayer, views.PhysicalEdgeList, views.PhysicalEdgeDetail, views.PhysicalEdgeDocument, views.PhysicalEdgeCreate,
        views.PhysicalEdgeUpdate, views.PhysicalEdgeDelete, views.PhysicalEdgeJsonList, views.PhysicalEdgeFormatList,
        views.LandEdgeLayer, views.LandEdgeList, views.LandEdgeDetail, views.LandEdgeDocument, views.LandEdgeCreate,
        views.LandEdgeUpdate, views.LandEdgeDelete, views.LandEdgeJsonList, views.LandEdgeFormatList,
        views.CompetenceEdgeLayer, views.CompetenceEdgeList, views.CompetenceEdgeDetail, views.CompetenceEdgeDocument, views.CompetenceEdgeCreate,
        views.CompetenceEdgeUpdate, views.CompetenceEdgeDelete, views.CompetenceEdgeJsonList, views.CompetenceEdgeFormatList,
        views.WorkManagementEdgeLayer, views.WorkManagementEdgeList, views.WorkManagementEdgeDetail, views.WorkManagementEdgeDocument, views.WorkManagementEdgeCreate,
        views.WorkManagementEdgeUpdate, views.WorkManagementEdgeDelete, views.WorkManagementEdgeJsonList, views.WorkManagementEdgeFormatList,
        views.SignageManagementEdgeLayer, views.SignageManagementEdgeList, views.SignageManagementEdgeDetail, views.SignageManagementEdgeDocument, views.SignageManagementEdgeCreate,
        views.SignageManagementEdgeUpdate, views.SignageManagementEdgeDelete, views.SignageManagementEdgeJsonList, views.SignageManagementEdgeFormatList,
    )
)
