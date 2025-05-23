# Generated by Django 4.2.20 on 2025-05-05 10:16

from django.db import migrations


def fill_reports_assigned_handlers(apps, schema_editor):
    """
    For unresolved reports that have been assigned to a user, set their
    assigned_handler as the current_user.
    """
    Report = apps.get_model("feedback", "Report")

    reports = Report.objects.select_related("status").exclude(
        current_user__isnull=True,
        status__identifier__in=["solved_intervention", "solved"],
    )
    for report in reports:
        report.assigned_handler = report.current_user
        report.save()


class Migration(migrations.Migration):
    dependencies = [
        ("feedback", "0045_report_use_current_user_and_assigned_handler"),
    ]

    operations = [
        migrations.RunPython(fill_reports_assigned_handlers, migrations.RunPython.noop)
    ]
