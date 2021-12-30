import json
from geotrek.feedback.models import ReportStatus
from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def suricate_management_enabled():
    return settings.SURICATE_MANAGEMENT_ENABLED


@register.simple_tag
def status_ids():
    status_ids = {
        status.pk: str(status.suricate_id)
        for status in ReportStatus.objects.all()
    }
    return json.dumps(status_ids)
