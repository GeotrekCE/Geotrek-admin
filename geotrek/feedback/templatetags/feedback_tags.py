import json
from geotrek.feedback.models import PredefinedEmail, ReportStatus, WorkflowManager
from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def suricate_management_enabled():
    return settings.SURICATE_MANAGEMENT_ENABLED


@register.simple_tag
def app_title():
    return settings.TITLE


@register.simple_tag
def suricate_workflow_enabled():
    return settings.SURICATE_WORKFLOW_ENABLED


@register.simple_tag
def enable_report_colors_per_status():
    return settings.ENABLE_REPORT_COLORS_PER_STATUS


@register.simple_tag
def status_ids_and_colors():
    status_ids_and_colors = {
        status.pk: {
            "label": str(status.label),
            "id": str(status.identifier),
            "color": str(status.color),
            "display_in_legend": status.display_in_legend
        }
        for status in ReportStatus.objects.all()
    }
    return json.dumps(status_ids_and_colors)


@register.simple_tag
def predefined_emails():
    predefined_emails = {
        email.pk: {
            "label": str(email.label),
            "text": str(email.text)
        }
        for email in PredefinedEmail.objects.all()
    }
    return json.dumps(predefined_emails)


@register.simple_tag
def resolved_intervention_info(report):
    if report:
        username = "'?'"
        intervention = report.report_interventions().first()
        if intervention:
            authors = intervention.authors
            if authors:
                user = authors.last()  # oldest author is the one that created the intervention
                if user.profile and user.profile.extended_username:
                    username = user.profile.extended_username
                else:
                    username = user.username

            resolved_intervention_info = {
                "date": report.interventions.first().date.strftime("%d/%m/%Y") if report.interventions else None,
                "username": username
            }
            return json.dumps(resolved_intervention_info)
    return json.dumps({})


@register.simple_tag
def workflow_manager():
    if WorkflowManager.objects.exists():
        return WorkflowManager.objects.first().user.pk
    return None
