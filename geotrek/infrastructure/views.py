from django.utils.decorators import method_decorator

from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, MapEntityFormat,
                             MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete)

from geotrek.authent.decorators import same_structure_required, editor_required
from geotrek.core.models import AltimetryMixin
from .models import Infrastructure, Signage
from .filters import InfrastructureFilter, SignageFilter
from .forms import InfrastructureForm, SignageForm


class InfrastructureLayer(MapEntityLayer):
    queryset = Infrastructure.objects.existing()
    properties = ['name']


class InfrastructureList(MapEntityList):
    queryset = Infrastructure.objects.existing()
    filterform = InfrastructureFilter
    columns = ['id', 'name', 'type', 'cities']


class InfrastructureJsonList(MapEntityJsonList, InfrastructureList):
    pass


class InfrastructureFormatList(MapEntityFormat, InfrastructureList):
    columns = InfrastructureList.columns + AltimetryMixin.COLUMNS


class InfrastructureDetail(MapEntityDetail):
    queryset = Infrastructure.objects.existing()

    def can_edit(self):
        return self.request.user.is_superuser or (
            hasattr(self.request.user, 'profile') and
            self.request.user.profile.is_editor and
            self.get_object().same_structure(self.request.user))


class InfrastructureDocument(MapEntityDocument):
    model = Infrastructure


class InfrastructureCreate(MapEntityCreate):
    model = Infrastructure
    form_class = InfrastructureForm

    @method_decorator(editor_required('infrastructure:infrastructure_list'))
    def dispatch(self, *args, **kwargs):
        return super(InfrastructureCreate, self).dispatch(*args, **kwargs)


class InfrastructureUpdate(MapEntityUpdate):
    queryset = Infrastructure.objects.existing()
    form_class = InfrastructureForm

    @method_decorator(editor_required('infrastructure:infrastructure_detail'))
    @same_structure_required('infrastructure:infrastructure_detail')
    def dispatch(self, *args, **kwargs):
        return super(InfrastructureUpdate, self).dispatch(*args, **kwargs)


class InfrastructureDelete(MapEntityDelete):
    model = Infrastructure

    @method_decorator(editor_required('infrastructure:infrastructure_detail'))
    @same_structure_required('infrastructure:infrastructure_detail')
    def dispatch(self, *args, **kwargs):
        return super(InfrastructureDelete, self).dispatch(*args, **kwargs)


class SignageLayer(MapEntityLayer):
    queryset = Signage.objects.existing()
    properties = ['name']


class SignageList(MapEntityList):
    queryset = Signage.objects.existing()
    filterform = SignageFilter
    columns = ['id', 'name', 'type', 'cities']


class SignageJsonList(MapEntityJsonList, SignageList):
    pass


class SignageFormatList(MapEntityFormat, SignageList):
    columns = SignageList.columns + AltimetryMixin.COLUMNS


class SignageDetail(MapEntityDetail):
    queryset = Signage.objects.existing()

    def can_edit(self):
        return self.request.user.is_superuser or (
            hasattr(self.request.user, 'profile') and
            self.request.user.profile.is_editor and
            self.get_object().same_structure(self.request.user))


class SignageDocument(MapEntityDocument):
    model = Signage


class SignageCreate(MapEntityCreate):
    model = Signage
    form_class = SignageForm

    @method_decorator(editor_required('infrastructure:signage_list'))
    def dispatch(self, *args, **kwargs):
        return super(SignageCreate, self).dispatch(*args, **kwargs)


class SignageUpdate(MapEntityUpdate):
    queryset = Signage.objects.existing()
    form_class = SignageForm

    @method_decorator(editor_required('infrastructure:signage_detail'))
    @same_structure_required('infrastructure:signage_detail')
    def dispatch(self, *args, **kwargs):
        return super(SignageUpdate, self).dispatch(*args, **kwargs)


class SignageDelete(MapEntityDelete):
    model = Signage

    @method_decorator(editor_required('infrastructure:signage_detail'))
    @same_structure_required('infrastructure:signage_detail')
    def dispatch(self, *args, **kwargs):
        return super(SignageDelete, self).dispatch(*args, **kwargs)
