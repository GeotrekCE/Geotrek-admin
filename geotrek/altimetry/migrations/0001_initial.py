# Generated by Django 3.1.5 on 2021-01-11 17:24

import django.contrib.gis.db.models.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Dem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True, serialize=False, db_column="rid"
                    ),
                ),
                (
                    "rast",
                    django.contrib.gis.db.models.fields.RasterField(srid=settings.SRID),
                ),
            ],
        ),
    ]
