from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from mapentity import views as mapentity_views

from geotrek.feedback import models as feedback_models


class ReportLayer(mapentity_views.MapEntityLayer):
    model = feedback_models.Report
    properties = ['name']


class ReportList(mapentity_views.MapEntityList):
    model = feedback_models.Report
    columns = ['id', 'name', 'email', 'category', 'date_insert']


class CategoryList(mapentity_views.JSONResponseMixin, ListView):
    model = feedback_models.ReportCategory

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CategoryList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        return [{'label': c.category} for c in self.object_list]
