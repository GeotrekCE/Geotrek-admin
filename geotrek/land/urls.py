from django.conf.urls import patterns, url

from mapentity import registry

from . import models
from . import views


urlpatterns = patterns('',
    url(r'^api/city/city.geojson$', views.CityGeoJSONLayer.as_view(), name="city_layer"), 
    url(r'^api/restrictedarea/restrictedarea.geojson$', views.RestrictedAreaGeoJSONLayer.as_view(), name="restrictedarea_layer"), 
    url(r'^api/district/district.geojson$', views.DistrictGeoJSONLayer.as_view(), name="district_layer"), 
)

urlpatterns += registry.register(models.PhysicalEdge, menu=False)
urlpatterns += registry.register(models.LandEdge, menu=False)
urlpatterns += registry.register(models.CompetenceEdge, menu=False)
urlpatterns += registry.register(models.WorkManagementEdge, menu=False)
urlpatterns += registry.register(models.SignageManagementEdge, menu=False)
