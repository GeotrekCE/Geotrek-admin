# Generated by Django 3.2.15 on 2022-11-10 10:28

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0025_auto_20220425_1550"),
        ("tourism", "0012_auto_20200708_1448"),
    ]

    operations = [
        migrations.AddField(
            model_name="filetype",
            name="date_insert",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Insertion date",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="filetype",
            name="date_update",
            field=models.DateTimeField(
                auto_now=True, db_index=True, verbose_name="Update date"
            ),
        ),
        migrations.AddField(
            model_name="label",
            name="date_insert",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Insertion date",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="label",
            name="date_update",
            field=models.DateTimeField(
                auto_now=True, db_index=True, verbose_name="Update date"
            ),
        ),
        migrations.AddField(
            model_name="organism",
            name="date_insert",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Insertion date",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="organism",
            name="date_update",
            field=models.DateTimeField(
                auto_now=True, db_index=True, verbose_name="Update date"
            ),
        ),
        migrations.AddField(
            model_name="recordsource",
            name="date_insert",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Insertion date",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="recordsource",
            name="date_update",
            field=models.DateTimeField(
                auto_now=True, db_index=True, verbose_name="Update date"
            ),
        ),
        migrations.AddField(
            model_name="reservationsystem",
            name="date_insert",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Insertion date",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="reservationsystem",
            name="date_update",
            field=models.DateTimeField(
                auto_now=True, db_index=True, verbose_name="Update date"
            ),
        ),
        migrations.AddField(
            model_name="targetportal",
            name="date_insert",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Insertion date",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="targetportal",
            name="date_update",
            field=models.DateTimeField(
                auto_now=True, db_index=True, verbose_name="Update date"
            ),
        ),
        migrations.AddField(
            model_name="theme",
            name="date_insert",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Insertion date",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="theme",
            name="date_update",
            field=models.DateTimeField(
                auto_now=True, db_index=True, verbose_name="Update date"
            ),
        ),
    ]
