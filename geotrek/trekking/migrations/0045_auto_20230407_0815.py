# Generated by Django 3.2.18 on 2023-04-07 08:15

import django.db.models.deletion
from django.db import migrations, models

import geotrek.authent.models


class Migration(migrations.Migration):
    dependencies = [
        ("authent", "0011_alter_userprofile_structure"),
        ("trekking", "0044_auto_20230406_1426"),
    ]

    operations = [
        migrations.AlterField(
            model_name="poi",
            name="structure",
            field=models.ForeignKey(
                default=geotrek.authent.models.default_structure_pk,
                on_delete=django.db.models.deletion.PROTECT,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="service",
            name="structure",
            field=models.ForeignKey(
                default=geotrek.authent.models.default_structure_pk,
                on_delete=django.db.models.deletion.PROTECT,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="trek",
            name="structure",
            field=models.ForeignKey(
                default=geotrek.authent.models.default_structure_pk,
                on_delete=django.db.models.deletion.PROTECT,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
    ]
