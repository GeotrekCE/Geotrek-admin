# Generated by Django 3.2.15 on 2022-11-18 13:21

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("diving", "0006_auto_20210122_1029"),
    ]

    operations = [
        migrations.AddField(
            model_name="practice",
            name="date_insert",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Insertion date",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="practice",
            name="date_update",
            field=models.DateTimeField(
                auto_now=True, db_index=True, verbose_name="Update date"
            ),
        ),
    ]
