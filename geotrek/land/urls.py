from django.conf import settings
from django.utils.translation import gettext as _
from mapentity.registry import registry, MapEntityOptions

from . import models

app_name = 'land'


class LandEdgeOptions(MapEntityOptions):
    def __init__(self, model):
        super().__init__(model)
        self.label = _("Land")


urlpatterns = registry.register(models.PhysicalEdge, menu=False)
urlpatterns += registry.register(models.LandEdge, options=LandEdgeOptions, menu=settings.TREKKING_TOPOLOGY_ENABLED and settings.LANDEDGE_MODEL_ENABLED)
urlpatterns += registry.register(models.CompetenceEdge, menu=False)
urlpatterns += registry.register(models.WorkManagementEdge, menu=False)
urlpatterns += registry.register(models.SignageManagementEdge, menu=False)
