# Generated by Django 3.1.14 on 2022-03-24 09:44

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("feedback", "0028_auto_20220316_0951"),
    ]

    operations = [
        migrations.RenameField(
            model_name="report",
            old_name="uid",
            new_name="external_uuid",
        ),
    ]
