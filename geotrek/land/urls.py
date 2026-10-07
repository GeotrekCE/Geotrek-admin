from mapentity.registry import registry

from . import entities, models

app_name = "land"

urlpatterns = registry.register(
    models.PhysicalEdge, options=entities.PhysicalEdgeOptions
)
urlpatterns += registry.register(models.LandEdge, options=entities.LandEdgeOptions)
urlpatterns += registry.register(
    models.CirculationEdge, options=entities.CirculationEdgeOptions
)
urlpatterns += registry.register(
    models.CompetenceEdge, options=entities.CompetenceEdgeOptions
)
urlpatterns += registry.register(
    models.WorkManagementEdge, options=entities.WorkManagementEdgeOptions
)
urlpatterns += registry.register(
    models.SignageManagementEdge, options=entities.SignageManagementEdgeOptions
)
urlpatterns += registry.register(
    models.Status,
    options=entities.StatusOptions,
)
