# Generated by Django 3.1.7 on 2021-03-15 15:12

from django.db import migrations


def flatten_geometrycollection(apps, schema_editor):
    Site = apps.get_model("outdoor", "Site")
    Course = apps.get_model("outdoor", "Course")
    Site.objects.bulk_update(Site.objects.all(), ["geom"])
    Course.objects.bulk_update(Course.objects.all(), ["geom"])


class Migration(migrations.Migration):
    dependencies = [
        ("outdoor", "0041_auto_20221110_1128"),
    ]

    operations = [
        migrations.RunPython(flatten_geometrycollection, migrations.RunPython.noop),
    ]
