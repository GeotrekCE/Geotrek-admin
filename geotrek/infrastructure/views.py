from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, MapEntityFormat,
                             MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete)

from geotrek.authent.decorators import same_structure_required
from geotrek.core.models import AltimetryMixin
from geotrek.core.views import CreateFromTopologyMixin

from .filters import InfrastructureFilterSet, SignageFilterSet
from .forms import InfrastructureForm, SignageForm
from .models import Infrastructure, Signage


class InfrastructureLayer(MapEntityLayer):
    queryset = Infrastructure.objects.existing()
    properties = ['name']


class InfrastructureList(MapEntityList):
    queryset = Infrastructure.objects.existing()
    filterform = InfrastructureFilterSet
    columns = ['id', 'name', 'type', 'state', 'cities']


class InfrastructureJsonList(MapEntityJsonList, InfrastructureList):
    pass


class InfrastructureFormatList(MapEntityFormat, InfrastructureList):
    columns = [
        'id', 'name', 'type', 'state', 'description',
        'structure', 'date_insert', 'date_update',
        'cities', 'districts', 'areas',
    ] + AltimetryMixin.COLUMNS


class InfrastructureDetail(MapEntityDetail):
    queryset = Infrastructure.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super(InfrastructureDetail, self).get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class InfrastructureDocument(MapEntityDocument):
    model = Infrastructure


class InfrastructureCreate(CreateFromTopologyMixin, MapEntityCreate):
    model = Infrastructure
    form_class = InfrastructureForm

    def get_form(self, form_class):
        """
        customize form in generic view
        """
        form = super(InfrastructureCreate, self).get_form(form_class)

        if not self.request.user.has_perm('infrastructure.add_infrastructurestate'):
            form.fields['state'].queryset = self.request.user.profile.structure.infrastructurestate_set.all()

        return form


class InfrastructureUpdate(MapEntityUpdate):
    queryset = Infrastructure.objects.existing()
    form_class = InfrastructureForm

    @same_structure_required('infrastructure:infrastructure_detail')
    def dispatch(self, *args, **kwargs):
        return super(InfrastructureUpdate, self).dispatch(*args, **kwargs)

    def get_form(self, form_class):
        """
        customize form in generic view
        """
        form = super(InfrastructureUpdate, self).get_form(form_class)

        if not self.request.user.has_perm('infrastructure.add_infrastructurestate'):
            form.fields['state'].queryset = self.request.user.profile.structure.infrastructurestate_set.all()

        return form


class InfrastructureDelete(MapEntityDelete):
    model = Infrastructure

    @same_structure_required('infrastructure:infrastructure_detail')
    def dispatch(self, *args, **kwargs):
        return super(InfrastructureDelete, self).dispatch(*args, **kwargs)


class SignageLayer(MapEntityLayer):
    queryset = Signage.objects.existing()
    properties = ['name']


class SignageList(MapEntityList):
    queryset = Signage.objects.existing()
    filterform = SignageFilterSet
    columns = ['id', 'name', 'type', 'state', 'cities']


class SignageJsonList(MapEntityJsonList, SignageList):
    pass


class SignageFormatList(MapEntityFormat, SignageList):
    columns = [
        'id', 'name', 'type', 'state', 'description',
        'structure', 'date_insert', 'date_update',
        'cities', 'districts', 'areas',
    ] + AltimetryMixin.COLUMNS


class SignageDetail(MapEntityDetail):
    queryset = Signage.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super(SignageDetail, self).get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class SignageDocument(MapEntityDocument):
    model = Signage


class SignageCreate(MapEntityCreate):
    model = Signage
    form_class = SignageForm

    def get_form(self, form_class):
        """
        customize form in generic view
        """
        form = super(SignageCreate, self).get_form(form_class)

        if not self.request.user.has_perm('infrastructure.add_infrastructurestate'):
            form.fields['state'].queryset = self.request.user.profile.structure.infrastructurestate_set.all()

        return form


class SignageUpdate(MapEntityUpdate):
    queryset = Signage.objects.existing()
    form_class = SignageForm

    @same_structure_required('infrastructure:signage_detail')
    def dispatch(self, *args, **kwargs):
        return super(SignageUpdate, self).dispatch(*args, **kwargs)

    def get_form(self, form_class):
        """
        customize form in generic view
        """
        form = super(SignageUpdate, self).get_form(form_class)

        if not self.request.user.has_perm('infrastructure.add_infrastructurestate'):
            form.fields['state'].queryset = self.request.user.profile.structure.infrastructurestate_set.all()

        return form


class SignageDelete(MapEntityDelete):
    model = Signage

    @same_structure_required('infrastructure:signage_detail')
    def dispatch(self, *args, **kwargs):
        return super(SignageDelete, self).dispatch(*args, **kwargs)
