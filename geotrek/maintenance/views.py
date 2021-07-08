
import logging

from django.conf import settings
from django.db.models import Subquery, OuterRef
from django.utils.translation import gettext_lazy as _
from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, MapEntityFormat, MapEntityViewSet,
                             MapEntityDetail, MapEntityDocument, MapEntityCreate, MapEntityUpdate, MapEntityDelete)

from geotrek.altimetry.models import AltimetryMixin
from geotrek.common.mixins import CustomColumnsMixin
from geotrek.common.views import FormsetMixin
from geotrek.authent.decorators import same_structure_required
from .models import Intervention, Project, ManDay
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


class InterventionList(CustomColumnsMixin, MapEntityList):
    queryset = Intervention.objects.existing()
    filterform = InterventionFilterSet
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['date', 'type', 'target', 'status', 'stake']


class InterventionJsonList(MapEntityJsonList, InterventionList):
    pass


class InterventionFormatList(MapEntityFormat, InterventionList):

    all_mandays = ManDay.objects.all()  # Used to find all jobs that ARE USED in interventions

    def build_cost_column_name(self, job_name):
        return f"{_('Cost')} {job_name}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if settings.ENABLE_JOB_COST_DETAILED_EXPORT:
            jobs_as_names = list(set(self.all_mandays.values_list('job__job', flat=True)))  # All jobs that are used in interventions, as unique names
            cost_column_names = map(self.build_cost_column_name, jobs_as_names)   # Column names for each job cost
            self.mandatory_columns.extend(cost_column_names)  # Add these column names to export

    def get_queryset(self):
        queryset = Intervention.objects.existing()
        if settings.ENABLE_JOB_COST_DETAILED_EXPORT:
            jobs_used_in_interventions = list(set(self.all_mandays.values_list('job__job', 'job_id')))  # All jobs that are used in interventions, as unique names and ids
            for job_name, job_id in jobs_used_in_interventions:
                column_name = self.build_cost_column_name(job_name)
                # Create subquery to retrieve manday object for a given intervention and a given job
                manday_query = ManDay.objects.filter(intervention=OuterRef('pk'), job_id=job_id)
                # Use this subquery to calculate cost for a given intervention and a given job, thanks to manday subquery result
                subquery = (Subquery((manday_query.values('nb_days'))) * Subquery((manday_query.values('job__cost'))))
                # Annotate queryset with this cost query
                params = {column_name: subquery}
                queryset = queryset.annotate(**params)
        return queryset

    mandatory_columns = ['id']

    default_extra_columns = [
        'name', 'date', 'type', 'target', 'status', 'stake',
        'disorders', 'total_manday', 'project', 'subcontracting',
        'width', 'height', 'length', 'area', 'structure',
        'description', 'date_insert', 'date_update',
        'material_cost', 'heliport_cost', 'subcontract_cost',
        'total_cost_mandays', 'total_cost',
        'cities', 'districts', 'areas',
    ] + AltimetryMixin.COLUMNS


class InterventionDetail(MapEntityDetail):
    queryset = Intervention.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
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
        return super().dispatch(*args, **kwargs)


class InterventionDelete(MapEntityDelete):
    model = Intervention

    @same_structure_required('maintenance:intervention_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


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
        return super().get_queryset().filter(pk__in=nonemptyqs)


class ProjectList(CustomColumnsMixin, MapEntityList):
    queryset = Project.objects.existing()
    filterform = ProjectFilterSet
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['period', 'type', 'domain']


class ProjectJsonList(MapEntityJsonList, ProjectList):
    pass


class ProjectFormatList(MapEntityFormat, ProjectList):
    mandatory_columns = ['id']
    default_extra_columns = [
        'structure', 'name', 'period', 'type', 'domain', 'constraint', 'global_cost',
        'interventions', 'interventions_total_cost', 'comments', 'contractors',
        'project_owner', 'project_manager', 'founders',
        'date_insert', 'date_update',
        'cities', 'districts', 'areas',
    ]


class ProjectDetail(MapEntityDetail):
    queryset = Project.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
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
        return super().dispatch(*args, **kwargs)


class ProjectDelete(MapEntityDelete):
    model = Project

    @same_structure_required('maintenance:project_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ProjectViewSet(MapEntityViewSet):
    model = Project
    queryset = Project.objects.existing()
    serializer_class = ProjectSerializer
    geojson_serializer_class = ProjectGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        # Override annotation done by MapEntityViewSet.get_queryset()
        return Project.objects.all()
