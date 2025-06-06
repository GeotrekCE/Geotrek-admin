# Generated by Django 3.2.18 on 2023-04-07 09:47

import django.db.models.deletion
from django.db import migrations, models

import geotrek.authent.models


class Migration(migrations.Migration):
    dependencies = [
        ("authent", "0011_alter_userprofile_structure"),
        ("core", "0034_auto_20220909_1316"),
    ]

    operations = [
        migrations.AlterField(
            model_name="certificationlabel",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="certificationstatus",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="certificationtrail",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="comfort",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="network",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="path",
            name="comfort",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="paths",
                to="core.comfort",
                verbose_name="Comfort",
            ),
        ),
        migrations.AlterField(
            model_name="path",
            name="source",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="paths",
                to="core.pathsource",
                verbose_name="Source",
            ),
        ),
        migrations.AlterField(
            model_name="path",
            name="stake",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="paths",
                to="core.stake",
                verbose_name="Maintenance stake",
            ),
        ),
        migrations.AlterField(
            model_name="path",
            name="structure",
            field=models.ForeignKey(
                default=geotrek.authent.models.default_structure_pk,
                on_delete=django.db.models.deletion.PROTECT,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="pathsource",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="stake",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="trail",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.trailcategory",
                verbose_name="Category",
            ),
        ),
        migrations.AlterField(
            model_name="trail",
            name="structure",
            field=models.ForeignKey(
                default=geotrek.authent.models.default_structure_pk,
                on_delete=django.db.models.deletion.PROTECT,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="trailcategory",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="usage",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
    ]
