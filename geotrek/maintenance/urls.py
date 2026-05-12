from django.conf import settings
from mapentity.registry import registry

from . import models

app_name = "maintenance"
urlpatterns = registry.register(
    models.Intervention, menu=settings.INTERVENTION_MODEL_ENABLED
)
urlpatterns += registry.register(models.Project, menu=settings.PROJECT_MODEL_ENABLED)
