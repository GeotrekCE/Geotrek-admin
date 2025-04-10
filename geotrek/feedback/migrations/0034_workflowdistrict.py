# Generated by Django 3.1.14 on 2022-04-12 12:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("zoning", "0100_initial"),
        ("feedback", "0033_auto_20220328_0931"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkflowDistrict",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "district",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="zoning.district",
                    ),
                ),
            ],
            options={
                "verbose_name": "Workflow District",
                "verbose_name_plural": "Workflow Districts",
            },
        ),
    ]
