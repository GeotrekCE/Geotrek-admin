import logging

from crispy_forms.helper import FormHelper
from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.db.models import CharField, F, Value
from django.db.models.functions import Concat
from django.urls.base import reverse
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from mapentity import views as mapentity_views
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from geotrek.common.mixins.views import CustomColumnsMixin
from geotrek.common.viewsets import GeotrekMapentityViewSet

from . import models as feedback_models
from . import serializers as feedback_serializers
from .filters import ReportEmailFilterSet, ReportFilterSet
from .forms import ReportForm

logger = logging.getLogger(__name__)


class ReportList(CustomColumnsMixin, mapentity_views.MapEntityList):
    queryset = (
        feedback_models.Report.objects.existing()
        .select_related(
            "activity",
            "category",
            "problem_magnitude",
            "status",
            "related_trek",
            "assigned_user",
        )
        .prefetch_related("attachments")
    )
    model = feedback_models.Report
    mandatory_columns = ["id", "eid", "activity"]
    default_extra_columns = ["category", "status", "date_update"]
    searchable_columns = ["id", "eid"]

    def get_queryset(self):
        qs = super().get_queryset()  # Filtered by FilterSet
        if (
            settings.SURICATE_WORKFLOW_ENABLED
            and not settings.SURICATE_WORKFLOW_SETTINGS.get("SKIP_MANAGER_MODERATION")
            and not (
                self.request.user.is_superuser
                or self.request.user.pk
                in list(
                    feedback_models.WorkflowManager.objects.values_list(
                        "user", flat=True
                    )
                )
            )
        ):
            qs = qs.filter(assigned_user=self.request.user)
        return qs


class ReportFilter(mapentity_views.MapEntityFilter):
    model = feedback_models.Report
    filterset_class = ReportEmailFilterSet

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Remove email from available filters in workflow mode for supervisors
        if settings.SURICATE_WORKFLOW_ENABLED and not (
            self.request.user.is_superuser
            or self.request.user.pk
            in list(
                feedback_models.WorkflowManager.objects.values_list("user", flat=True)
            )
        ):
            self._filterform = ReportFilterSet()
            self._filterform.helper = FormHelper()
            self._filterform.helper.field_class = "form-control-sm"
            self._filterform.helper.submit = None
        context["filter"] = self._filterform
        return context


class ReportFormatList(mapentity_views.MapEntityFormat, ReportList):
    mandatory_columns = ["id", "email"]
    filterset_class = ReportEmailFilterSet
    default_extra_columns = [
        "activity",
        "comment",
        "category",
        "problem_magnitude",
        "status",
        "related_trek",
        "date_insert",
        "date_update",
        "assigned_user",
        "provider",
    ]

    def get_columns(self):
        """Override columns to remove email if user is noy superuser nor in workflow managers"""
        columns = super().get_columns()
        if not self.request.user.is_superuser:
            if (
                settings.SURICATE_WORKFLOW_ENABLED
                and not feedback_models.WorkflowManager.objects.filter(
                    user_id=self.request.user.pk
                ).exists()
            ):
                columns.remove("email")
        return columns


class ReportCreate(mapentity_views.MapEntityCreate):
    model = feedback_models.Report
    form_class = ReportForm

    def get_success_url(self):
        if settings.SURICATE_WORKFLOW_ENABLED:
            return reverse("feedback:report_list")
        return super().get_success_url()


class ReportUpdate(mapentity_views.MapEntityUpdate):
    queryset = (
        feedback_models.Report.objects.existing()
        .select_related(
            "activity", "category", "problem_magnitude", "status", "related_trek"
        )
        .prefetch_related("attachments")
    )
    form_class = ReportForm


class ReportViewSet(GeotrekMapentityViewSet):
    model = feedback_models.Report
    serializer_class = feedback_serializers.ReportSerializer
    geojson_serializer_class = feedback_serializers.ReportGeojsonSerializer
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_class = ReportEmailFilterSet
    mapentity_list_class = ReportList

    def get_queryset(self):
        qs = self.model.objects.existing().select_related("status")
        if not self.request.user.is_superuser:
            if (
                settings.SURICATE_WORKFLOW_ENABLED
                and not settings.SURICATE_WORKFLOW_SETTINGS.get(
                    "SKIP_MANAGER_MODERATION"
                )
                and not feedback_models.WorkflowManager.objects.filter(
                    user_id=self.request.user.pk
                ).exists()
            ):
                qs = qs.filter(assigned_user=self.request.user)

        if self.format_kwarg == "geojson":
            number = "eid" if settings.SURICATE_WORKFLOW_ENABLED else "id"
            qs = qs.annotate(
                name=Concat(
                    Value(_("Report")), Value(" "), F(number), output_field=CharField()
                ),
                api_geom=Transform("geom", settings.API_SRID),
            )
            qs = qs.only("id", "status")
            return qs

        qs = qs.select_related(
            "activity", "category", "problem_magnitude", "related_trek"
        ).prefetch_related("attachments")
        return qs

    def view_cache_key(self):
        """Used by the ``view_cache_response_content`` decorator."""
        language = get_language()
        geojson_lookup = None
        latest_saved = feedback_models.Report.latest_updated()
        if latest_saved:
            geojson_lookup = "%s_report_%s_%s_geojson_layer" % (
                language,
                latest_saved.isoformat(),
                self.request.user.pk if settings.SURICATE_WORKFLOW_ENABLED else "",
            )
        return geojson_lookup
