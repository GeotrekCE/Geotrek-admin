# Generated by Django 1.11.27 on 2020-02-11 10:11

import django.db.models.deletion
from django.db import migrations, models

import geotrek.authent.models


class Migration(migrations.Migration):
    dependencies = [
        ("infrastructure", "0016_auto_20191029_1110"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="infrastructurecondition",
            options={
                "ordering": ("label",),
                "verbose_name": "Infrastructure Condition",
                "verbose_name_plural": "Infrastructure Conditions",
            },
        ),
        migrations.AlterField(
            model_name="infrastructure",
            name="condition",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="infrastructure.InfrastructureCondition",
                verbose_name="Condition",
            ),
        ),
        migrations.AlterField(
            model_name="infrastructure",
            name="description",
            field=models.TextField(
                blank=True, help_text="Specificites", verbose_name="Description"
            ),
        ),
        migrations.AlterField(
            model_name="infrastructure",
            name="eid",
            field=models.CharField(
                blank=True, max_length=1024, null=True, verbose_name="External id"
            ),
        ),
        migrations.AlterField(
            model_name="infrastructure",
            name="implantation_year",
            field=models.PositiveSmallIntegerField(
                null=True, verbose_name="Implantation year"
            ),
        ),
        migrations.AlterField(
            model_name="infrastructure",
            name="name",
            field=models.CharField(
                help_text="Reference, code, ...", max_length=128, verbose_name="Name"
            ),
        ),
        migrations.AlterField(
            model_name="infrastructure",
            name="structure",
            field=models.ForeignKey(
                default=geotrek.authent.models.default_structure_pk,
                on_delete=django.db.models.deletion.CASCADE,
                to="authent.Structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="infrastructure",
            name="topo_object",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="core.Topology",
            ),
        ),
        migrations.AlterField(
            model_name="infrastructure",
            name="type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="infrastructure.InfrastructureType",
                verbose_name="Type",
            ),
        ),
        migrations.AlterField(
            model_name="infrastructurecondition",
            name="label",
            field=models.CharField(max_length=250, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="infrastructurecondition",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="authent.Structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="infrastructuretype",
            name="label",
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name="infrastructuretype",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="authent.Structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="infrastructuretype",
            name="type",
            field=models.CharField(
                choices=[("A", "Building"), ("E", "Facility")], max_length=1
            ),
        ),
        migrations.AlterModelTable(
            name="infrastructure",
            table=None,
        ),
        migrations.AlterModelTable(
            name="infrastructurecondition",
            table=None,
        ),
        migrations.AlterModelTable(
            name="infrastructuretype",
            table=None,
        ),
    ]
