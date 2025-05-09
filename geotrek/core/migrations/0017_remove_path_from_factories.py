# Generated by Django 2.0.13 on 2020-04-06 13:40

from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from django.db import migrations


def remove_generated_paths_factories(apps, schema_editor):
    PathModel = apps.get_model("core", "Path")
    PathModel.objects.filter(
        geom=LineString(
            Point(700000, 6600000), Point(700100, 6600100), srid=settings.SRID
        )
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0016_auto_20200406_1340"),
    ]

    operations = [migrations.RunPython(remove_generated_paths_factories)]
