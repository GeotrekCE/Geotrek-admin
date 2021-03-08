import logging

from django.utils.translation import gettext_lazy as _
from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, MapEntityFormat, MapEntityViewSet,
                             MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete)

from geotrek.altimetry.models import AltimetryMixin
from geotrek.common.views import FormsetMixin
from geotrek.authent.decorators import same_structure_required
from .models import Intervention, Project
from .filters import InterventionFilterSet, ProjectFilterSet
from .forms import (InterventionForm, ProjectForm,
                    FundingFormSet, ManDayFormSet)
from .serializers import (InterventionSerializer, ProjectSerializer,
                          InterventionGeojsonSerializer, ProjectGeojsonSerializer)
from rest_framework import permissions as rest_permissions


logger = logging.getLogger(__name__)


class InterventionLayer(MapEntityLayer):
    queryset = Intervention.objects.existing()
    filterform = InterventionFilterSet
    properties = ['name']


class InterventionList(MapEntityList):
    queryset = Intervention.objects.existing()
    filterform = InterventionFilterSet
    columns = ['id', 'name', 'date', 'type', 'target', 'status', 'stake']


class InterventionJsonList(MapEntityJsonList, InterventionList):
    pass


class InterventionFormatList(MapEntityFormat, InterventionList):
    columns = [
        'id', 'name', 'date', 'type', 'target', 'status', 'stake',
        'disorders', 'total_manday', 'project', 'subcontracting',
        'width', 'height', 'length', 'area', 'structure',
        'description', 'date_insert', 'date_update',
        'material_cost', 'heliport_cost', 'subcontract_cost',
        'total_cost_mandays', 'total_cost',
    ] + AltimetryMixin.COLUMNS

    def get_queryset(self):
        return super().get_queryset() \
            .select_related('type', 'target_type', 'status', 'stake', 'project', 'structure') \
            .prefetch_related('jobs', 'disorders')


class InterventionDetail(MapEntityDetail):
    queryset = Intervention.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super(InterventionDetail, self).get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class InterventionDocument(MapEntityDocument):
    model = Intervention


class ManDayFormsetMixin(FormsetMixin):
    context_name = 'manday_formset'
    formset_class = ManDayFormSet


class InterventionCreate(ManDayFormsetMixin, MapEntityCreate):
    model = Intervention
    form_class = InterventionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'target_id' in self.request.GET and 'target_type' in self.request.GET:
            # Create intervention on an existing infrastructure
            kwargs['target_id'] = self.request.GET['target_id']
            kwargs['target_type'] = self.request.GET['target_type']
        return kwargs


class InterventionUpdate(ManDayFormsetMixin, MapEntityUpdate):
    queryset = Intervention.objects.existing()
    form_class = InterventionForm

    @same_structure_required('maintenance:intervention_detail')
    def dispatch(self, *args, **kwargs):
        return super(InterventionUpdate, self).dispatch(*args, **kwargs)


class InterventionDelete(MapEntityDelete):
    model = Intervention

    @same_structure_required('maintenance:intervention_detail')
    def dispatch(self, *args, **kwargs):
        return super(InterventionDelete, self).dispatch(*args, **kwargs)


class InterventionViewSet(MapEntityViewSet):
    model = Intervention
    queryset = Intervention.objects.existing()
    serializer_class = InterventionSerializer
    geojson_serializer_class = InterventionGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        # Override annotation done by MapEntityViewSet.get_queryset()
        return Intervention.objects.all()


class ProjectLayer(MapEntityLayer):
    queryset = Project.objects.existing()
    properties = ['name']

    def get_queryset(self):
        nonemptyqs = Intervention.objects.existing().filter(project__isnull=False).values('project')
        return super(ProjectLayer, self).get_queryset().filter(pk__in=nonemptyqs)


class ProjectList(MapEntityList):
    queryset = Project.objects.existing()
    filterform = ProjectFilterSet
    columns = ['id', 'name', 'period', 'type', 'domain']


class ProjectJsonList(MapEntityJsonList, ProjectList):
    pass


class ProjectFormatList(MapEntityFormat, ProjectList):
    columns = [
        'id', 'structure', 'name', 'period', 'type', 'domain', 'constraint', 'global_cost',
        'interventions', 'interventions_total_cost', 'comments', 'contractors',
        'project_owner', 'project_manager', 'founders',
        'date_insert', 'date_update',
    ]

    def get_queryset(self):
        return super().get_queryset() \
            .select_related('structure', 'type', 'project_owner', 'project_manager', 'founders')


class ProjectDetail(MapEntityDetail):
    queryset = Project.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectDetail, self).get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        context['empty_map_message'] = _("No intervention related.")
        return context


class ProjectDocument(MapEntityDocument):
    model = Project


class FundingFormsetMixin(FormsetMixin):
    context_name = 'funding_formset'
    formset_class = FundingFormSet


class ProjectCreate(FundingFormsetMixin, MapEntityCreate):
    model = Project
    form_class = ProjectForm


class ProjectUpdate(FundingFormsetMixin, MapEntityUpdate):
    queryset = Project.objects.existing()
    form_class = ProjectForm

    @same_structure_required('maintenance:project_detail')
    def dispatch(self, *args, **kwargs):
        return super(ProjectUpdate, self).dispatch(*args, **kwargs)


class ProjectDelete(MapEntityDelete):
    model = Project

    @same_structure_required('maintenance:project_detail')
    def dispatch(self, *args, **kwargs):
        return super(ProjectDelete, self).dispatch(*args, **kwargs)


class ProjectViewSet(MapEntityViewSet):
    model = Project
    queryset = Project.objects.existing()
    serializer_class = ProjectSerializer
    geojson_serializer_class = ProjectGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        # Override annotation done by MapEntityViewSet.get_queryset()
        return Project.objects.all()
