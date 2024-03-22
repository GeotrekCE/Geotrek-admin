from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from geotrek.flatpages import models as flatpages_models

from .forms import FlatPageForm


class FlatPageEditMixin:
    model = flatpages_models.FlatPage
    form_class = FlatPageForm
    success_url = reverse_lazy('admin:flatpages_flatpage_changelist')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class FlatPageCreate(FlatPageEditMixin, CreateView):
    pass


class FlatPageUpdate(FlatPageEditMixin, UpdateView):
    pass
