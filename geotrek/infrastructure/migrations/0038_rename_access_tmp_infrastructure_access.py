# Generated by Django 3.2.21 on 2023-12-04 09:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("infrastructure", "0037_remove_infrastructure_access"),
    ]

    operations = [
        migrations.RenameField(
            model_name="infrastructure",
            old_name="access_tmp",
            new_name="access",
        ),
    ]
