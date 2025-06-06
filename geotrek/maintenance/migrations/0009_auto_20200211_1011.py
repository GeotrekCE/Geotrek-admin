# Generated by Django 1.11.27 on 2020-02-11 10:11

import datetime

import django.db.models.deletion
from django.db import migrations, models

import geotrek.authent.models


class Migration(migrations.Migration):
    dependencies = [
        ("maintenance", "0008_auto_20191210_0921"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contractor",
            name="contractor",
            field=models.CharField(max_length=128, verbose_name="Contractor"),
        ),
        migrations.AlterField(
            model_name="contractor",
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
            model_name="funding",
            name="amount",
            field=models.FloatField(default=0.0, verbose_name="Amount"),
        ),
        migrations.AlterField(
            model_name="funding",
            name="organism",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="common.Organism",
                verbose_name="Organism",
            ),
        ),
        migrations.AlterField(
            model_name="funding",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="maintenance.Project",
                verbose_name="Project",
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="area",
            field=models.FloatField(
                blank=True, default=0, editable=False, null=True, verbose_name="Area"
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="ascent",
            field=models.IntegerField(
                blank=True, default=0, editable=False, null=True, verbose_name="Ascent"
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="date",
            field=models.DateField(
                default=datetime.datetime.now, help_text="When ?", verbose_name="Date"
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="descent",
            field=models.IntegerField(
                blank=True, default=0, editable=False, null=True, verbose_name="Descent"
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="description",
            field=models.TextField(
                blank=True, help_text="Remarks and notes", verbose_name="Description"
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="disorders",
            field=models.ManyToManyField(
                blank=True,
                related_name="interventions",
                to="maintenance.InterventionDisorder",
                verbose_name="Disorders",
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="height",
            field=models.FloatField(
                blank=True, default=0.0, null=True, verbose_name="Height"
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="heliport_cost",
            field=models.FloatField(
                blank=True, default=0.0, null=True, verbose_name="Heliport cost"
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="length",
            field=models.FloatField(
                blank=True, default=0.0, null=True, verbose_name="3D Length"
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="material_cost",
            field=models.FloatField(
                blank=True, default=0.0, null=True, verbose_name="Material cost"
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="max_elevation",
            field=models.IntegerField(
                blank=True,
                default=0,
                editable=False,
                null=True,
                verbose_name="Maximum elevation",
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="min_elevation",
            field=models.IntegerField(
                blank=True,
                default=0,
                editable=False,
                null=True,
                verbose_name="Minimum elevation",
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="name",
            field=models.CharField(
                help_text="Brief summary", max_length=128, verbose_name="Name"
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="project",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="interventions",
                to="maintenance.Project",
                verbose_name="Project",
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="slope",
            field=models.FloatField(
                blank=True, default=0.0, editable=False, null=True, verbose_name="Slope"
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="stake",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="interventions",
                to="core.Stake",
                verbose_name="Stake",
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="status",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="maintenance.InterventionStatus",
                verbose_name="Status",
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="structure",
            field=models.ForeignKey(
                default=geotrek.authent.models.default_structure_pk,
                on_delete=django.db.models.deletion.CASCADE,
                to="authent.Structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="subcontract_cost",
            field=models.FloatField(
                blank=True, default=0.0, null=True, verbose_name="Subcontract cost"
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="subcontracting",
            field=models.BooleanField(default=False, verbose_name="Subcontracting"),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="maintenance.InterventionType",
                verbose_name="Type",
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="width",
            field=models.FloatField(
                blank=True, default=0.0, null=True, verbose_name="Width"
            ),
        ),
        migrations.AlterField(
            model_name="interventiondisorder",
            name="disorder",
            field=models.CharField(max_length=128, verbose_name="Disorder"),
        ),
        migrations.AlterField(
            model_name="interventiondisorder",
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
            model_name="interventionjob",
            name="cost",
            field=models.DecimalField(
                decimal_places=2, default=1.0, max_digits=8, verbose_name="Cost"
            ),
        ),
        migrations.AlterField(
            model_name="interventionjob",
            name="job",
            field=models.CharField(max_length=128, verbose_name="Job"),
        ),
        migrations.AlterField(
            model_name="interventionjob",
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
            model_name="interventionstatus",
            name="order",
            field=models.PositiveSmallIntegerField(
                blank=True, default=None, null=True, verbose_name="Display order"
            ),
        ),
        migrations.AlterField(
            model_name="interventionstatus",
            name="status",
            field=models.CharField(max_length=128, verbose_name="Status"),
        ),
        migrations.AlterField(
            model_name="interventionstatus",
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
            model_name="interventiontype",
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
            model_name="interventiontype",
            name="type",
            field=models.CharField(max_length=128, verbose_name="Type"),
        ),
        migrations.AlterField(
            model_name="manday",
            name="intervention",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="maintenance.Intervention",
            ),
        ),
        migrations.AlterField(
            model_name="manday",
            name="job",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="maintenance.InterventionJob",
                verbose_name="Job",
            ),
        ),
        migrations.AlterField(
            model_name="manday",
            name="nb_days",
            field=models.DecimalField(
                decimal_places=2, max_digits=6, verbose_name="Mandays"
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="begin_year",
            field=models.IntegerField(verbose_name="Begin year"),
        ),
        migrations.AlterField(
            model_name="project",
            name="comments",
            field=models.TextField(
                blank=True, help_text="Remarks and notes", verbose_name="Comments"
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="constraint",
            field=models.TextField(
                blank=True,
                help_text="Specific conditions, ...",
                verbose_name="Constraint",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="contractors",
            field=models.ManyToManyField(
                blank=True,
                related_name="projects",
                to="maintenance.Contractor",
                verbose_name="Contractors",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="domain",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="maintenance.ProjectDomain",
                verbose_name="Domain",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="end_year",
            field=models.IntegerField(blank=True, null=True, verbose_name="End year"),
        ),
        migrations.AlterField(
            model_name="project",
            name="global_cost",
            field=models.FloatField(
                blank=True,
                default=0,
                help_text="€",
                null=True,
                verbose_name="Global cost",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="name",
            field=models.CharField(max_length=128, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="project",
            name="project_manager",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="manage",
                to="common.Organism",
                verbose_name="Project manager",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="project_owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="own",
                to="common.Organism",
                verbose_name="Project owner",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="structure",
            field=models.ForeignKey(
                default=geotrek.authent.models.default_structure_pk,
                on_delete=django.db.models.deletion.CASCADE,
                to="authent.Structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="maintenance.ProjectType",
                verbose_name="Type",
            ),
        ),
        migrations.AlterField(
            model_name="projectdomain",
            name="domain",
            field=models.CharField(max_length=128, verbose_name="Domain"),
        ),
        migrations.AlterField(
            model_name="projectdomain",
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
            model_name="projecttype",
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
            model_name="projecttype",
            name="type",
            field=models.CharField(max_length=128, verbose_name="Type"),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="deleted",
            field=models.BooleanField(
                default=False, editable=False, verbose_name="Deleted"
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="deleted",
            field=models.BooleanField(
                default=False, editable=False, verbose_name="Deleted"
            ),
        ),
        migrations.AlterModelTable(
            name="contractor",
            table=None,
        ),
        migrations.AlterModelTable(
            name="funding",
            table=None,
        ),
        migrations.AlterModelTable(
            name="intervention",
            table=None,
        ),
        migrations.AlterModelTable(
            name="interventiondisorder",
            table=None,
        ),
        migrations.AlterModelTable(
            name="interventionjob",
            table=None,
        ),
        migrations.AlterModelTable(
            name="interventionstatus",
            table=None,
        ),
        migrations.AlterModelTable(
            name="interventiontype",
            table=None,
        ),
        migrations.AlterModelTable(
            name="manday",
            table=None,
        ),
        migrations.AlterModelTable(
            name="project",
            table=None,
        ),
        migrations.AlterModelTable(
            name="projectdomain",
            table=None,
        ),
        migrations.AlterModelTable(
            name="projecttype",
            table=None,
        ),
    ]
