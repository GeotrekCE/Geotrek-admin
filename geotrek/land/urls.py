from mapentity import registry

from . import models


urlpatterns = registry.register(models.PhysicalEdge, menu=False)
urlpatterns += registry.register(models.LandEdge)
urlpatterns += registry.register(models.CompetenceEdge, menu=False)
urlpatterns += registry.register(models.WorkManagementEdge, menu=False)
urlpatterns += registry.register(models.SignageManagementEdge, menu=False)
