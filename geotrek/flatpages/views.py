from urlparse import urljoin

from rest_framework import permissions as rest_permissions
from rest_framework import viewsets

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView

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
        qs = flatpages_models.FlatPage.objects.filter(published=True)

        if self.request.GET.get('source', '') != '':
            qs = qs.filter(source__name__in=self.request.GET['source'].split(','))

        if self.request.GET.get('portal', '') != '':
            qs = qs.filter(portal__name__in=self.request.GET['portal'].split(','))

        return qs


class FlatPageEditMixin(object):
    model = flatpages_models.FlatPage
    form_class = FlatPageForm
    success_url = reverse_lazy('admin:flatpages_flatpage_changelist')

    def get_form_kwargs(self):
        kwargs = super(FlatPageEditMixin, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class FlatPageCreate(FlatPageEditMixin, CreateView):
    pass


class FlatPageUpdate(FlatPageEditMixin, UpdateView):
    pass


class FlatPageMeta(DetailView):
    model = flatpages_models.FlatPage
    template_name = 'flatpages/flatpage_meta.html'

    def get_context_data(self, **kwargs):
        context = super(FlatPageMeta, self).get_context_data(**kwargs)
        context['FACEBOOK_APP_ID'] = settings.FACEBOOK_APP_ID
        context['facebook_image'] = urljoin(self.request.GET['rando_url'], settings.FACEBOOK_IMAGE)
        context['FACEBOOK_IMAGE_WIDTH'] = settings.FACEBOOK_IMAGE_WIDTH
        context['FACEBOOK_IMAGE_HEIGHT'] = settings.FACEBOOK_IMAGE_HEIGHT
        return context
