from django.conf import settings
from mapentity.registry import registry, MapEntityOptions

from . import models

app_name = 'land'


class LandEdgeOptions(MapEntityOptions):
    """
    Overwrite options for Statuses module to redirect to LandEdge objects
    """
    def __init__(self, model):
        super().__init__(model)
        self.url_list = 'land:landedge_list'
        self.url_add = 'land:landedge_add'
        self.icon = 'images/landedge.png'
        self.icon_small = 'images/landedge-16.png'
        self.icon_big = 'images/landedge-96.png'


urlpatterns = registry.register(models.PhysicalEdge, menu=False)
urlpatterns += registry.register(models.LandEdge, menu=False)
urlpatterns += registry.register(models.CirculationEdge, menu=False)
urlpatterns += registry.register(models.Status, options=LandEdgeOptions, menu=settings.TREKKING_TOPOLOGY_ENABLED and settings.LANDEDGE_MODEL_ENABLED)
urlpatterns += registry.register(models.CompetenceEdge, menu=False)
urlpatterns += registry.register(models.WorkManagementEdge, menu=False)
urlpatterns += registry.register(models.SignageManagementEdge, menu=False)
