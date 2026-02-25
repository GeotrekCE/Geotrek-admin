from mapentity.registry import registry

from . import entities, models

app_name = "maintenance"

urlpatterns = registry.register(
    models.Intervention, options=entities.InterventionEntityOptions
)
urlpatterns += registry.register(models.Project, options=entities.ProjectEntityOptions)
