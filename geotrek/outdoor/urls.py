from mapentity.registry import registry

from . import entities, models

app_name = "outdoor"

urlpatterns = []

urlpatterns += registry.register(models.Site, options=entities.SiteEntityOptions)
urlpatterns += registry.register(models.Course, options=entities.CourseEntityOptions)
