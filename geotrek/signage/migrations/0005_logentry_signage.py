from django.db import migrations
from django.db.models import CharField
from django.db.models.functions import Cast


def logentry_signage(apps, schema_editor):
    LogEntryModel = apps.get_model("mapentity", "LogEntry")

    ContentTypeModel = apps.get_model("contenttypes", "ContentType")
    SignageModel = apps.get_model("signage", "Signage")
    signage = ContentTypeModel.objects.get(app_label="signage", model="signage")
    logentries = LogEntryModel.objects.filter(
        content_type__model="baseinfrastructure",
        object_id__in=SignageModel.objects.all()
        .annotate(as_str=Cast("id", CharField(max_length=99)))
        .values_list("as_str", flat=True),
    )
    logentries.update(content_type=signage)


class Migration(migrations.Migration):
    dependencies = [
        ("signage", "0004_attachments_signage"),
        ("mapentity", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(logentry_signage),
    ]
