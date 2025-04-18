# Generated by Django 3.1.13 on 2021-10-22 12:52

import uuid

from django.db import migrations


def gen_uuid(apps, schema_editor):
    MyModel = apps.get_model("core", "Topology")
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save(update_fields=["uuid"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0027_topology_uuid"),
    ]

    operations = [
        migrations.RunPython(gen_uuid),
    ]
