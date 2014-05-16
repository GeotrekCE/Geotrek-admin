from mapentity import registry

from geotrek.feedback import models as feedback_models


urlpatterns = registry.register(feedback_models.Report)
