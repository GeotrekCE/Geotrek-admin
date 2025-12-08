from django.db import migrations
from django.db.models import CharField
from django.db.models.functions import Cast


def logentry_infrastructure(apps, schema_editor):
    LogEntryModel = apps.get_model("mapentity", "LogEntry")

    ContentTypeModel = apps.get_model("contenttypes", "ContentType")
    InfrastructureModel = apps.get_model("infrastructure", "Infrastructure")
    infrastructure = ContentTypeModel.objects.get(
        app_label="infrastructure", model="infrastructure"
    )
    logentries = LogEntryModel.objects.filter(
        content_type__model="baseinfrastructure",
        object_id__in=InfrastructureModel.objects.all()
        .annotate(as_str=Cast("id", CharField(max_length=99)))
        .values_list("as_str", flat=True),
    )
    logentries.update(content_type=infrastructure)


class Migration(migrations.Migration):
    dependencies = [
        ("mapentity", "0001_initial"),
        ("infrastructure", "0013_attachments_infrastructure"),
    ]

    operations = [
        migrations.RunPython(logentry_infrastructure),
    ]
