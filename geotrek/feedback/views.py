from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.views.generic.list import ListView
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from mapentity import views as mapentity_views

from geotrek.common.models import Attachment, FileType
from geotrek.feedback.filters import ReportFilterSet
from geotrek.feedback import models as feedback_models
from geotrek.feedback import serializers as feedback_serializers


class ReportLayer(mapentity_views.MapEntityLayer):
    model = feedback_models.Report
    filterform = ReportFilterSet
    properties = ['email']


class ReportList(mapentity_views.MapEntityList):
    model = feedback_models.Report
    filterform = ReportFilterSet
    columns = [
        'id', 'email', 'activity', 'category',
        'status', 'date_update',
    ]


class ReportJsonList(mapentity_views.MapEntityJsonList, ReportList):
    pass


class ReportFormatList(mapentity_views.MapEntityFormat, ReportList):
    columns = [
        'id', 'email', 'activity', 'comment', 'category',
        'problem_magnitude', 'status', 'related_trek',
        'date_insert', 'date_update',
    ]


class CategoryList(mapentity_views.JSONResponseMixin, ListView):
    model = feedback_models.ReportCategory

    def dispatch(self, *args, **kwargs):
        return super(CategoryList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        return [{'id': c.id,
                 'label': c.label} for c in self.object_list]


class FeedbackOptionsView(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, *args, **kwargs):
        categories = feedback_models.ReportCategory.objects.all()
        cat_serializer = feedback_serializers.ReportCategorySerializer(categories, many=True)
        activities = feedback_models.ReportActivity.objects.all()
        activities_serializer = feedback_serializers.ReportActivitySerializer(activities, many=True)
        magnitude_problems = feedback_models.ReportProblemMagnitude.objects.all()
        mag_serializer = feedback_serializers.ReportProblemMagnitudeSerializer(magnitude_problems, many=True)

        options = {
            "categories": cat_serializer.data,
            "activities": activities_serializer.data,
            "magnitudeProblems": mag_serializer.data
        }

        return Response(options)


class ReportViewSet(mapentity_views.MapEntityViewSet):
    """Disable permissions requirement"""
    model = feedback_models.Report
    queryset = feedback_models.Report.objects.all()
    parser_classes = [FormParser, MultiPartParser]
    serializer_class = feedback_serializers.ReportSerializer
    geojson_serializer_class = feedback_serializers.ReportGeojsonSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def report(self, request, lang=None):
        response = super(ReportViewSet, self).create(request)
        creator, created = get_user_model().objects.get_or_create(username='feedback', defaults={'is_active': False})
        for file in request._request.FILES.values():
            Attachment.objects.create(
                filetype=FileType.objects.get_or_create(type=settings.REPORT_FILETYPE)[0],
                content_type=ContentType.objects.get(id=feedback_models.Report.get_content_type_id()),
                object_id=response.data.get('id'),
                creator=creator,
                attachment_file=file
            )
        if settings.SEND_REPORT_ACK and response.status_code == 201:
            send_mail(
                _("Geotrek : Signal a mistake"),
                _("""Hello,

We acknowledge receipt of your feedback, thank you for your interest in Geotrek.

Best regards,

The Geotrek Team
http://www.geotrek.fr"""),
                settings.DEFAULT_FROM_EMAIL,
                [request.data.get('email')]
            )
        return response
