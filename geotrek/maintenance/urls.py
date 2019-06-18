from django.conf import settings

from mapentity.registry import registry

from . import models


urlpatterns = registry.register(models.Intervention, menu=settings.TREKKING_TOPOLOGY_ENABLED)
urlpatterns += registry.register(models.Project, menu=settings.TREKKING_TOPOLOGY_ENABLED)
