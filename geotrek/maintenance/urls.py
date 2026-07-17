from django.conf import settings
from django.urls import path
from mapentity.registry import registry

from . import entities, models, views

app_name = "maintenance"

urlpatterns = [
    path(
        "api/intervention/references/",
        views.InterventionReferences.as_view(),
        name="intervention_references",
    ),
]

urlpatterns += registry.register(
    models.Intervention, options=entities.InterventionEntityOptions
)
urlpatterns += registry.register(models.Project, options=entities.ProjectEntityOptions)
