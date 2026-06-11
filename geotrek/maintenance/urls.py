from django.conf import settings
from django.urls import path
from mapentity.registry import registry

from . import models, views

app_name = "maintenance"
urlpatterns = [
    path(
        "api/intervention/references/",
        views.InterventionReferences.as_view(),
        name="intervention_references",
    ),
]

urlpatterns += registry.register(
    models.Intervention, menu=settings.INTERVENTION_MODEL_ENABLED
)
urlpatterns += registry.register(models.Project, menu=settings.PROJECT_MODEL_ENABLED)
