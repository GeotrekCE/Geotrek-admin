from django.conf.urls import patterns

from .views import (
    InterventionLayer, InterventionList, InterventionDetail, InterventionDocument, InterventionCreate,
    InterventionUpdate, InterventionDelete, InterventionJsonList, InterventionFormatList,
    ProjectLayer, ProjectList, ProjectDetail, ProjectDocument, ProjectCreate,
    ProjectUpdate, ProjectDelete, ProjectJsonList, ProjectFormatList,
)

from geotrek.mapentity.urlizor import view_classes_to_url


urlpatterns = patterns('', *view_classes_to_url(
    InterventionLayer, InterventionList, InterventionDetail, InterventionDocument, InterventionCreate,
    InterventionUpdate, InterventionDelete, InterventionJsonList, InterventionFormatList,
    ProjectLayer, ProjectList, ProjectDetail, ProjectDocument, ProjectCreate,
    ProjectUpdate, ProjectDelete, ProjectJsonList, ProjectFormatList,
))
