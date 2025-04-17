import logging
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from PIL import Image
from rest_framework.mixins import CreateModelMixin
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from geotrek.api.v2 import serializers as api_serializers
from geotrek.api.v2 import viewsets as api_viewsets
from geotrek.common.models import Attachment, FileType
from geotrek.feedback import models as feedback_models

logger = logging.getLogger(__name__)


class ReportStatusViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.ReportStatusSerializer
    queryset = feedback_models.ReportStatus.objects.order_by(
        "pk"
    )  # Required for reliable pagination


class ReportCategoryViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.ReportCategorySerializer
    queryset = feedback_models.ReportCategory.objects.order_by(
        "pk"
    )  # Required for reliable pagination


class ReportActivityViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.ReportActivitySerializer
    queryset = feedback_models.ReportActivity.objects.order_by(
        "pk"
    )  # Required for reliable pagination


class ReportProblemMagnitudeViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.ReportProblemMagnitudeSerializer
    queryset = feedback_models.ReportProblemMagnitude.objects.order_by(
        "pk"
    )  # Required for reliable pagination


class ReportViewSet(GenericViewSet, CreateModelMixin):
    model = feedback_models.Report
    parser_classes = [FormParser, MultiPartParser]
    serializer_class = api_serializers.ReportAPISerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request)
        creator, created = get_user_model().objects.get_or_create(
            username="feedback", defaults={"is_active": False}
        )
        for file in request._request.FILES.values():
            attachment = Attachment(
                filetype=FileType.objects.get_or_create(type=settings.REPORT_FILETYPE)[
                    0
                ],
                content_type=ContentType.objects.get_for_model(feedback_models.Report),
                object_id=response.data.get("id"),
                creator=creator,
                attachment_file=file,
            )
            name, extension = os.path.splitext(file.name)
            try:
                attachment.full_clean()  # Check that file extension and mimetypes are allowed
            except ValidationError as e:
                logger.error(
                    "Invalid attachment %s%s for report %s: %s",
                    name,
                    extension,
                    response.data.get("id"),
                    str(e),
                )
            else:
                try:
                    # Reencode file to bitmap then back to jpeg lfor safety
                    if not os.path.exists(f"{settings.TMP_DIR}/report_file/"):
                        os.mkdir(f"{settings.TMP_DIR}/report_file/")
                    tmp_bmp_path = os.path.join(
                        f"{settings.TMP_DIR}/report_file/", f"{name}.bmp"
                    )
                    tmp_jpeg_path = os.path.join(
                        f"{settings.TMP_DIR}/report_file/", f"{name}.jpeg"
                    )
                    Image.open(file).save(tmp_bmp_path)
                    Image.open(tmp_bmp_path).save(tmp_jpeg_path)
                    with open(tmp_jpeg_path, "rb") as converted_file:
                        attachment.attachment_file = File(
                            converted_file, name=f"{name}.jpeg"
                        )
                        attachment.save()
                    os.remove(tmp_bmp_path)
                    os.remove(tmp_jpeg_path)
                except Exception as e:
                    logger.error(
                        "Failed to convert attachment %s%s for report %s: %s",
                        name,
                        extension,
                        response.data.get("id"),
                        str(e),
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
