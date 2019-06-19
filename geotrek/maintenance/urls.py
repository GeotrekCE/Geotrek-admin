from django.conf import settings

from mapentity.registry import registry

from . import models


urlpatterns = registry.register(models.Intervention)
urlpatterns += registry.register(models.Project)
