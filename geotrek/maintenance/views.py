import logging
import re

from django.conf import settings
from django.db.models import Subquery, OuterRef, Sum
from django.db.models.expressions import Value
from django.utils.translation import gettext_lazy as _
from mapentity.views import (MapEntityList, MapEntityFormat, MapEntityDetail, MapEntityDocument,
                             MapEntityCreate, MapEntityUpdate, MapEntityDelete)

from geotrek.altimetry.models import AltimetryMixin
from geotrek.authent.decorators import same_structure_required
from geotrek.common.mixins.forms import FormsetMixin
from geotrek.common.mixins.views import CustomColumnsMixin
from geotrek.common.viewsets import GeotrekMapentityViewSet
from .filters import InterventionFilterSet, ProjectFilterSet
from .forms import (InterventionForm, ProjectForm,
                    FundingFormSet, ManDayFormSet)
from .models import Intervention, Project, ManDay
from .serializers import (InterventionSerializer, ProjectSerializer,
                          InterventionGeojsonSerializer, ProjectGeojsonSerializer)

logger = logging.getLogger(__name__)


ANNOTATION_FORBIDDEN_CHARS = re.compile(r"['`\"\]\[;\s]|--|/\*|\*/")
REPLACEMENT_CHAR = "_"


def _normalize_annotation_column_name(col_name):
    return ANNOTATION_FORBIDDEN_CHARS.sub(repl=REPLACEMENT_CHAR, string=col_name)


class InterventionList(CustomColumnsMixin, MapEntityList):
    queryset = Intervention.objects.existing()
    filterform = InterventionFilterSet
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['begin_date', 'end_date', 'type', 'target', 'status', 'stake']
    searchable_columns = ['id', 'name']
    unorderable_columns = ['target']


class InterventionFormatList(MapEntityFormat, InterventionList):

    @classmethod
    def build_cost_column_name(cls, job_name):
        return _normalize_annotation_column_name(f"{_('Cost')} {job_name}")

    def get_queryset(self):
        """Returns all interventions joined with a new column for each job, to record the total cost of each job in each intervention"""

        queryset = super().get_queryset()

        if settings.ENABLE_JOBS_COSTS_DETAILED_EXPORT:

            # Get all jobs that are used in interventions, as unique names, ids and costs
            all_mandays = ManDay.objects.all()
            jobs_used_in_interventions = list(
                set(all_mandays.values_list("job__job", "job_id", "job__cost"))
            )

            # Iter over unique jobs
            for job_name, job_id, job_cost in jobs_used_in_interventions:

                # Create column name for current job cost
                column_name = self.build_cost_column_name(job_name)

                # Create subquery to retrieve total cost of mandays for a given intervention and a given job
                mandays_query = (
                    ManDay.objects.filter(intervention=OuterRef("pk"), job_id=job_id)  # Extract all mandays for a given intervention and a given job
                    .values("job_id")  # Group by job
                    .annotate(total_days=Sum("nb_days"))  # Select number of days worked
                    .values("total_days")  # Rename result as total_days
                )

                # Use total_days and job cost to calculate total cost for a given intervention and a given job
                job_cost_query = Subquery(mandays_query) * Value(job_cost)

                # Annotate queryset with this cost query
                params = {column_name: job_cost_query}
                queryset = queryset.annotate(**params)
        return queryset

    @classmethod
    def get_mandatory_columns(cls):
        mandatory_columns = ['id']
        if settings.ENABLE_JOBS_COSTS_DETAILED_EXPORT:
            all_mandays = ManDay.objects.all()  # Used to find all jobs that ARE USED in interventions
            # Get all jobs that are used in interventions, as unique names
            jobs_as_names = list(
                set(all_mandays.values_list("job__job", flat=True))
            )
            # Create column names for each unique job cost
            cost_column_names = list(map(cls.build_cost_column_name, jobs_as_names))
            # Add these column names to export
            mandatory_columns = mandatory_columns + cost_column_names
        return mandatory_columns

    default_extra_columns = [
        'name', 'begin_date', 'end_date', 'type', 'target', 'status', 'stake',
        'disorders', 'total_manday', 'project', 'contractors', 'subcontracting',
        'width', 'height', 'area', 'structure',
        'description', 'date_insert', 'date_update',
        'material_cost', 'heliport_cost', 'contractor_cost',
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # If deletion is allowed
        if kwargs['can_delete']:
            intervention = self.get_object()
            # Disallow deletion if this intervention is part of Suricate Workflow at the moment
            not_workflow = not settings.SURICATE_WORKFLOW_ENABLED
            is_report = intervention.target and intervention.target.__class__.__name__ == "Report"
            report_is_closed = False
            if is_report:
                report_is_closed = (intervention.target.status.identifier == 'solved')
            kwargs["can_delete"] = not_workflow or (not is_report) or report_is_closed
        return kwargs


class InterventionDelete(MapEntityDelete):
    model = Intervention

    @same_structure_required('maintenance:intervention_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class InterventionViewSet(GeotrekMapentityViewSet):
    model = Intervention
    serializer_class = InterventionSerializer
    geojson_serializer_class = InterventionGeojsonSerializer
    filterset_class = InterventionFilterSet
    mapentity_list_class = InterventionList

    def get_queryset(self):
        qs = self.model.objects.existing()
        if self.format_kwarg == 'geojson':
            qs = qs.only('id', 'name')
        else:
            qs = qs.select_related("stake", "status", "type", "target_type").prefetch_related('target')
        return qs


class ProjectList(CustomColumnsMixin, MapEntityList):
    queryset = Project.objects.existing()
    filterform = ProjectFilterSet
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['period', 'type', 'domain']
    searchable_columns = ['id', 'name']
    unorderable_columns = ['period', ]


class ProjectFormatList(MapEntityFormat, ProjectList):
    mandatory_columns = ['id']
    default_extra_columns = [
        'structure', 'name', 'period', 'type', 'domain', 'constraint', 'global_cost',
        'interventions', 'interventions_total_cost', 'comments', 'contractors', 'intervention_contractors',
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


class ProjectViewSet(GeotrekMapentityViewSet):
    model = Project
    serializer_class = ProjectSerializer
    geojson_serializer_class = ProjectGeojsonSerializer
    filterset_class = ProjectFilterSet
    mapentity_list_class = ProjectList

    def get_queryset(self):
        qs = self.model.objects.existing()
        if self.format_kwarg == 'geojson':
            non_empty_qs = Intervention.objects.existing().filter(project__isnull=False).values('project')
            qs = qs.filter(pk__in=non_empty_qs)
            qs = qs.only('id', 'name')
        return qs
