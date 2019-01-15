from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from crispy_forms.layout import Fieldset, Layout, Div, HTML

from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, MapEntityFormat,
                             MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete)

from geotrek.authent.decorators import same_structure_required
from geotrek.core.models import AltimetryMixin
from geotrek.common.views import FormsetMixin

from .filters import SignageFilterSet
from .forms import SignageForm, BladeFormset
from .models import Signage
from .serializers import SignageSerializer

from rest_framework import permissions as rest_permissions
from mapentity.views import MapEntityViewSet


class BaseBladeMixin(FormsetMixin):
    context_name = 'blade_formset'
    formset_class = BladeFormset


class SignageLayer(MapEntityLayer):
    queryset = Signage.objects.existing()
    properties = ['name', 'published']


class SignageList(MapEntityList):
    queryset = Signage.objects.existing()
    filterform = SignageFilterSet
    columns = ['id', 'name', 'type', 'condition', 'cities']


class SignageJsonList(MapEntityJsonList, SignageList):
    pass


class SignageFormatList(MapEntityFormat, SignageList):
    columns = [
        'id', 'name', 'type', 'condition', 'description',
        'implantation_year', 'published', 'structure', 'date_insert',
        'date_update', 'cities', 'districts', 'areas',
    ] + AltimetryMixin.COLUMNS


class SignageDetail(MapEntityDetail):
    queryset = Signage.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super(SignageDetail, self).get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class SignageDocument(MapEntityDocument):
    model = Signage


class SignageCreate(BaseBladeMixin, MapEntityCreate):
    model = Signage
    form_class = SignageForm


class SignageUpdate(BaseBladeMixin, MapEntityUpdate):
    queryset = Signage.objects.existing()
    form_class = SignageForm

    @same_structure_required('signage:signage_detail')
    def dispatch(self, *args, **kwargs):
        return super(SignageUpdate, self).dispatch(*args, **kwargs)


class SignageDelete(MapEntityDelete):
    model = Signage

    @same_structure_required('signage:signage_detail')
    def dispatch(self, *args, **kwargs):
        return super(SignageDelete, self).dispatch(*args, **kwargs)


class SignageViewSet(MapEntityViewSet):
    model = Signage
    serializer_class = SignageSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        return Signage.objects.existing().filter(published=True).transform(settings.API_SRID, field_name='geom')
