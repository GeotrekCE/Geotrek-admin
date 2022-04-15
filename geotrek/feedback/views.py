from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db.models.functions import Concat
from django.db.models import F, Value
from django.urls.base import reverse
from django.utils.translation import gettext as _
from django.views.generic.list import ListView
from mapentity import views as mapentity_views
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from geotrek.common.mixins.api import APIViewSet
from geotrek.common.mixins.views import CustomColumnsMixin
from geotrek.common.models import Attachment, FileType
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.feedback import models as feedback_models
from geotrek.feedback import serializers as feedback_serializers
from geotrek.feedback.filters import ReportFilterSet
from geotrek.feedback.forms import ReportForm


class ReportLayer(mapentity_views.MapEntityLayer):
    queryset = feedback_models.Report.objects.existing() \
        .select_related(
            "activity", "category", "problem_magnitude", "status", "related_trek", "assigned_user"
    )
    model = feedback_models.Report
    filterform = ReportFilterSet
    properties = ["name"]

    def get_queryset(self):
        qs = super().get_queryset()  # Filtered by FilterSet
        status_id = self.request.GET.get('_status_id')
        if status_id:
            qs = qs.filter(status__identifier=status_id)
        if settings.SURICATE_WORKFLOW_ENABLED and not (self.request.user.is_superuser or self.request.user.pk in list(feedback_models.WorkflowManager.objects.values_list('user', flat=True))):
            qs = qs.filter(assigned_user=self.request.user)
        # # get display name if name is undefined to display tooltip on map feature hover
        # # Can't use annotate because it doesn't allow to use a model field name
        # # Can't use Case(When) in qs.extra
        # if settings.SURICATE_WORKFLOW_ENABLED:
        #     qs = qs.extra(select={'label': "CASE WHEN eid IS NULL THEN CONCAT(%s || ' ' || id) ELSE CONCAT(%s || ' ' || eid) END"},
        #                   select_params=(_("Report"), ))
        # else:
        #     qs = qs.extra(select={'label': "CONCAT(%s || ' ' || id)"},
        #                   select_params=(_("Report"), ))
        qs = qs.annotate(name=Concat(Value(_("Report")), Value(" "), F('id')))
        return qs

    def view_cache_key(self):
        """Used by the ``view_cache_response_content`` decorator.
        """
        language = self.request.LANGUAGE_CODE
        status_id = self.request.GET.get('_status_id')
        geojson_lookup = None
        if status_id:
            latest_saved = feedback_models.Report.latest_updated_by_status(status_id)
        else:
            latest_saved = feedback_models.Report.latest_updated()
        if latest_saved:
            geojson_lookup = '%s_report_%s_%s_%s_geojson_layer' % (
                language,
                latest_saved.isoformat(),
                status_id if status_id else '',
                self.request.user.pk if settings.SURICATE_WORKFLOW_ENABLED else ''
            )
        return geojson_lookup


class ReportList(CustomColumnsMixin, mapentity_views.MapEntityList):
    queryset = (
        feedback_models.Report.objects.existing()
        .select_related(
            "activity", "category", "problem_magnitude", "status", "related_trek", "assigned_user"
        )
        .prefetch_related("attachments")
    )
    model = feedback_models.Report
    filterform = ReportFilterSet
    mandatory_columns = ['id', 'name', 'activity']
    default_extra_columns = ['category', 'status', 'date_update']
    searchable_columns = ['id', 'name']

    def get_queryset(self):
        qs = super().get_queryset()  # Filtered by FilterSet
        if settings.SURICATE_WORKFLOW_ENABLED and not (self.request.user.is_superuser or self.request.user.pk in list(feedback_models.WorkflowManager.objects.values_list('user', flat=True))):
            qs = qs.filter(assigned_user=self.request.user)
        qs = qs.annotate(name=Concat(Value(_("Report")), Value(" "), F('id')))
        return qs


class ReportFormatList(mapentity_views.MapEntityFormat, ReportList):
    mandatory_columns = ['id']
    default_extra_columns = [
        'email', 'activity', 'comment', 'category',
        'problem_magnitude', 'status', 'related_trek',
        'date_insert', 'date_update', 'assigned_user'
    ]


class CategoryList(mapentity_views.JSONResponseMixin, ListView):
    model = feedback_models.ReportCategory

    def get_context_data(self, **kwargs):
        return [{"id": c.id, "label": c.label} for c in self.object_list]


class FeedbackOptionsView(APIView):
    permission_classes = [
        AllowAny,
    ]

    def get(self, request, *args, **kwargs):
        categories = feedback_models.ReportCategory.objects.all()
        cat_serializer = feedback_serializers.ReportCategorySerializer(
            categories, many=True
        )
        activities = feedback_models.ReportActivity.objects.all()
        activities_serializer = feedback_serializers.ReportActivitySerializer(
            activities, many=True
        )
        magnitude_problems = feedback_models.ReportProblemMagnitude.objects.all()
        mag_serializer = feedback_serializers.ReportProblemMagnitudeSerializer(
            magnitude_problems, many=True
        )

        options = {
            "categories": cat_serializer.data,
            "activities": activities_serializer.data,
            "magnitudeProblems": mag_serializer.data,
        }

        return Response(options)


class ReportCreate(mapentity_views.MapEntityCreate):
    model = feedback_models.Report
    form_class = ReportForm

    def get_success_url(self):
        return reverse('feedback:report_list')


class ReportUpdate(mapentity_views.MapEntityUpdate):
    queryset = feedback_models.Report.objects.existing().select_related(
        "activity", "category", "problem_magnitude", "status", "related_trek"
    ).prefetch_related("attachments")
    form_class = ReportForm


class ReportViewSet(GeotrekMapentityViewSet):
    """Disable permissions requirement"""

    model = feedback_models.Report
    serializer_class = feedback_serializers.ReportSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_columns(self):
        return ReportList.mandatory_columns + settings.COLUMNS_LISTS.get('feedback_view',
                                                                         ReportList.default_extra_columns)

    def get_queryset(self):
        return self.model.objects.existing().select_related(
            "activity", "category", "problem_magnitude", "status", "related_trek"
        ).prefetch_related("attachments")


class ReportAPIViewSet(APIViewSet):
    queryset = feedback_models.Report.objects.existing()\
                              .select_related("activity", "category", "problem_magnitude", "status", "related_trek")\
                              .prefetch_related("attachments")
    parser_classes = [FormParser, MultiPartParser]
    serializer_class = feedback_serializers.ReportAPISerializer
    geojson_serializer_class = feedback_serializers.ReportAPIGeojsonSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            "activity", "category", "problem_magnitude", "status", "related_trek"
        )

    @action(detail=False, methods=["post"])
    def report(self, request, lang=None):
        response = super().create(request)
        creator, created = get_user_model().objects.get_or_create(
            username="feedback", defaults={"is_active": False}
        )
        for file in request._request.FILES.values():
            Attachment.objects.create(
                filetype=FileType.objects.get_or_create(type=settings.REPORT_FILETYPE)[
                    0
                ],
                content_type=ContentType.objects.get_for_model(feedback_models.Report),
                object_id=response.data.get("id"),
                creator=creator,
                attachment_file=file,
            )
        if settings.SEND_REPORT_ACK and response.status_code == 201:
            send_mail(
                _("Geotrek : Signal a mistake"),
                _(
                    """Hello,

We acknowledge receipt of your feedback, thank you for your interest in Geotrek.

Best regards,

The Geotrek Team
http://www.geotrek.fr"""
                ),
                settings.DEFAULT_FROM_EMAIL,
                [request.data.get("email")],
            )
        return response
