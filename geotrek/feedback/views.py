from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.urls.base import reverse
from django.utils.translation import gettext as _
from django.views.generic.list import ListView

from geotrek.common.mixins.api import APIViewSet
from geotrek.common.mixins.views import CustomColumnsMixin
from geotrek.common.models import Attachment, FileType
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.feedback import models as feedback_models
from geotrek.feedback import serializers as feedback_serializers
from geotrek.feedback.filters import ReportFilterSet
from geotrek.feedback.forms import ReportForm
from mapentity import views as mapentity_views
from mapentity.views.generic import MapEntityCreate
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class ReportLayer(mapentity_views.MapEntityLayer):
    queryset = feedback_models.Report.objects.existing()
    model = feedback_models.Report
    filterform = ReportFilterSet
    properties = ["email"]


class ReportList(CustomColumnsMixin, mapentity_views.MapEntityList):
    queryset = (
        feedback_models.Report.objects.existing()
        .select_related(
            "activity", "category", "problem_magnitude", "status", "related_trek"
        )
        .prefetch_related("attachments")
    )
    model = feedback_models.Report
    filterform = ReportFilterSet
    mandatory_columns = ['id', 'email', 'activity']
    default_extra_columns = ['category', 'status', 'date_update']


class ReportFormatList(mapentity_views.MapEntityFormat, ReportList):
    mandatory_columns = ['id']
    default_extra_columns = [
        'email', 'activity', 'comment', 'category',
        'problem_magnitude', 'status', 'related_trek',
        'date_insert', 'date_update',
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


class ReportCreate(MapEntityCreate):
    model = feedback_models.Report
    form_class = ReportForm

    def get_success_url(self):
        return reverse('feedback:report_list')


class ReportViewSet(GeotrekMapentityViewSet):
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
