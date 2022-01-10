import json
from geotrek.feedback.models import ReportStatus
from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def suricate_management_enabled():
    return settings.SURICATE_MANAGEMENT_ENABLED


@register.simple_tag
def status_ids_and_colors():
    status_ids_and_colors = {
        status.pk: {
            "id": str(status.suricate_id),
            "color": str(status.color)
        }
        for status in ReportStatus.objects.all()
    }
    return json.dumps(status_ids_and_colors)
