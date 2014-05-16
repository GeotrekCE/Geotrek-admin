from mapentity import views as mapentity_views

from geotrek.feedback import models as feedback_models


class ReportLayer(mapentity_views.MapEntityLayer):
    model = feedback_models.Report
    properties = ['name']


class ReportList(mapentity_views.MapEntityList):
    model = feedback_models.Report
    columns = ['id', 'name', 'email', 'category', 'date_insert']

