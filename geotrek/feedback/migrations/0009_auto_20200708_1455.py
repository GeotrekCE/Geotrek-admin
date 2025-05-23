# Generated by Django 2.2.14 on 2020-07-08 14:55

import django.db.models.deletion
from django.db import migrations, models

import geotrek.feedback.models


class Migration(migrations.Migration):
    dependencies = [
        ("feedback", "0008_auto_20200526_1419"),
    ]

    operations = [
        migrations.AlterField(
            model_name="report",
            name="status",
            field=models.ForeignKey(
                blank=True,
                default=geotrek.feedback.models.status_default,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="feedback.ReportStatus",
                verbose_name="Status",
            ),
        ),
    ]
