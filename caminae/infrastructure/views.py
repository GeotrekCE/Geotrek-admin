from django.utils.decorators import method_decorator

from caminae.authent.decorators import same_structure_required, path_manager_required
from caminae.mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, MapEntityFormat,
                                MapEntityDetail, MapEntityCreate, MapEntityUpdate, MapEntityDelete)
from .models import Infrastructure, Signage
from .filters import InfrastructureFilter, SignageFilter
from .forms import InfrastructureForm, SignageForm


class InfrastructureLayer(MapEntityLayer):
    queryset = Infrastructure.objects.existing()


class InfrastructureList(MapEntityList):
    queryset = Infrastructure.objects.existing()
    filterform = InfrastructureFilter
    columns = ['id', 'name', 'type']


class InfrastructureJsonList(MapEntityJsonList, InfrastructureList):
    pass


class InfrastructureFormatList(MapEntityFormat, InfrastructureList):
    pass


class InfrastructureDetail(MapEntityDetail):
    model = Infrastructure

    def can_edit(self):
        return self.request.user.profile.is_path_manager() and \
               self.get_object().same_structure(self.request.user)


class InfrastructureCreate(MapEntityCreate):
    model = Infrastructure
    form_class = InfrastructureForm

    @method_decorator(path_manager_required('infrastructure:infrastructure_list'))
    def dispatch(self, *args, **kwargs):
        return super(InfrastructureCreate, self).dispatch(*args, **kwargs)


class InfrastructureUpdate(MapEntityUpdate):
    model = Infrastructure
    form_class = InfrastructureForm

    @method_decorator(path_manager_required('infrastructure:infrastructure_detail'))
    @same_structure_required('infrastructure:infrastructure_detail')
    def dispatch(self, *args, **kwargs):
        return super(InfrastructureUpdate, self).dispatch(*args, **kwargs)


class InfrastructureDelete(MapEntityDelete):
    model = Infrastructure

    @method_decorator(path_manager_required('infrastructure:infrastructure_detail'))
    @same_structure_required('infrastructure:infrastructure_detail')
    def dispatch(self, *args, **kwargs):
        return super(InfrastructureDelete, self).dispatch(*args, **kwargs)


class SignageLayer(MapEntityLayer):
    queryset = Signage.objects.existing()


class SignageList(MapEntityList):
    queryset = Signage.objects.existing()
    filterform = SignageFilter
    columns = ['id', 'name', 'type']


class SignageJsonList(MapEntityJsonList, SignageList):
    pass


class SignageFormatList(MapEntityFormat, SignageList):
    pass


class SignageDetail(MapEntityDetail):
    model = Signage

    def can_edit(self):
        return self.request.user.profile.is_path_manager()


class SignageCreate(MapEntityCreate):
    model = Signage
    form_class = SignageForm

    @method_decorator(path_manager_required('infrastructure:signage_list'))
    def dispatch(self, *args, **kwargs):
        return super(SignageCreate, self).dispatch(*args, **kwargs)


class SignageUpdate(MapEntityUpdate):
    model = Signage
    form_class = SignageForm

    @method_decorator(path_manager_required('infrastructure:signage_detail'))
    def dispatch(self, *args, **kwargs):
        return super(SignageUpdate, self).dispatch(*args, **kwargs)


class SignageDelete(MapEntityDelete):
    model = Signage

    @method_decorator(path_manager_required('infrastructure:signage_detail'))
    def dispatch(self, *args, **kwargs):
        return super(SignageDelete, self).dispatch(*args, **kwargs)
