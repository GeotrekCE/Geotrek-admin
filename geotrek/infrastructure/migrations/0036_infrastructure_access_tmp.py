# Generated by Django 3.2.21 on 2023-12-01 16:32

import django.db.models.deletion
from django.db import migrations, models


def reset_accessmean_id(apps, schema_editor):
    Infrastructure = apps.get_model("infrastructure", "Infrastructure")
    Common_AccessMean = apps.get_model("common", "AccessMean")

    for infrastructure in Infrastructure.objects.filter(access__isnull=False):
        access, create = Common_AccessMean.objects.get_or_create(
            label=infrastructure.access.label
        )
        infrastructure.access_tmp = access
        infrastructure.save()


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0036_accessmean"),
        ("infrastructure", "0035_auto_20230613_0917"),
    ]

    operations = [
        migrations.AddField(
            model_name="infrastructure",
            name="access_tmp",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="common.accessmean",
                verbose_name="Access mean",
            ),
        ),
        migrations.RunPython(
            reset_accessmean_id, reverse_code=migrations.RunPython.noop
        ),
    ]
