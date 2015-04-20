from rest_framework import permissions as rest_permissions
from rest_framework import viewsets

from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView, UpdateView

from geotrek.flatpages.serializers import FlatPageSerializer
from geotrek.flatpages import models as flatpages_models

from .forms import FlatPageForm


class FlatPageViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing flat pages instances.
    """
    model = flatpages_models.FlatPage
    serializer_class = FlatPageSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        return flatpages_models.FlatPage.objects.filter(published=True)


class FlatPageCreate(CreateView):
    model = flatpages_models.FlatPage
    form_class = FlatPageForm
    success_url = reverse_lazy('admin:flatpages_flatpage_changelist')


class FlatPageUpdate(UpdateView):
    model = flatpages_models.FlatPage
    form_class = FlatPageForm
    success_url = reverse_lazy('admin:flatpages_flatpage_changelist')
