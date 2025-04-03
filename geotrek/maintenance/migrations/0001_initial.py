import datetime

import django.contrib.gis.db.models.fields
import mapentity.models
from django.conf import settings
from django.db import migrations, models

import geotrek.authent.models
import geotrek.common.mixins.models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0001_initial"),
        ("authent", "0001_initial"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Contractor",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "contractor",
                    models.CharField(
                        max_length=128,
                        verbose_name="Contractor",
                        db_column="prestataire",
                    ),
                ),
                (
                    "structure",
                    models.ForeignKey(
                        db_column="structure",
                        on_delete=django.db.models.deletion.CASCADE,
                        default=geotrek.authent.models.default_structure_pk,
                        verbose_name="Related structure",
                        to="authent.Structure",
                    ),
                ),
            ],
            options={
                "ordering": ["contractor"],
                "db_table": "m_b_prestataire",
                "verbose_name": "Contractor",
                "verbose_name_plural": "Contractors",
            },
        ),
        migrations.CreateModel(
            name="Funding",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "amount",
                    models.FloatField(
                        default=0.0, verbose_name="Amount", db_column="montant"
                    ),
                ),
                (
                    "organism",
                    models.ForeignKey(
                        db_column="organisme",
                        on_delete=django.db.models.deletion.CASCADE,
                        verbose_name="Organism",
                        to="common.Organism",
                    ),
                ),
            ],
            options={
                "db_table": "m_r_chantier_financement",
                "verbose_name": "Funding",
                "verbose_name_plural": "Fundings",
            },
        ),
        migrations.CreateModel(
            name="Intervention",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "date_insert",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Insertion date",
                        db_column="date_insert",
                    ),
                ),
                (
                    "date_update",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="Update date",
                        db_column="date_update",
                    ),
                ),
                (
                    "deleted",
                    models.BooleanField(
                        default=False,
                        verbose_name="Deleted",
                        editable=False,
                        db_column="supprime",
                    ),
                ),
                (
                    "geom_3d",
                    django.contrib.gis.db.models.fields.GeometryField(
                        dim=3,
                        default=None,
                        editable=False,
                        srid=settings.SRID,
                        null=True,
                        spatial_index=False,
                    ),
                ),
                (
                    "length",
                    models.FloatField(
                        db_column="longueur",
                        default=0.0,
                        editable=False,
                        blank=True,
                        null=True,
                        verbose_name="3D Length",
                    ),
                ),
                (
                    "ascent",
                    models.IntegerField(
                        db_column="denivelee_positive",
                        default=0,
                        editable=False,
                        blank=True,
                        null=True,
                        verbose_name="Ascent",
                    ),
                ),
                (
                    "descent",
                    models.IntegerField(
                        db_column="denivelee_negative",
                        default=0,
                        editable=False,
                        blank=True,
                        null=True,
                        verbose_name="Descent",
                    ),
                ),
                (
                    "min_elevation",
                    models.IntegerField(
                        db_column="altitude_minimum",
                        default=0,
                        editable=False,
                        blank=True,
                        null=True,
                        verbose_name="Minimum elevation",
                    ),
                ),
                (
                    "max_elevation",
                    models.IntegerField(
                        db_column="altitude_maximum",
                        default=0,
                        editable=False,
                        blank=True,
                        null=True,
                        verbose_name="Maximum elevation",
                    ),
                ),
                (
                    "slope",
                    models.FloatField(
                        db_column="pente",
                        default=0.0,
                        editable=False,
                        blank=True,
                        null=True,
                        verbose_name="Slope",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Brief summary",
                        max_length=128,
                        verbose_name="Name",
                        db_column="nom",
                    ),
                ),
                (
                    "date",
                    models.DateField(
                        default=datetime.datetime.now,
                        help_text="When ?",
                        verbose_name="Date",
                        db_column="date",
                    ),
                ),
                (
                    "subcontracting",
                    models.BooleanField(
                        default=False,
                        verbose_name="Subcontracting",
                        db_column="sous_traitance",
                    ),
                ),
                (
                    "width",
                    models.FloatField(
                        default=0.0, verbose_name="Width", db_column="largeur"
                    ),
                ),
                (
                    "height",
                    models.FloatField(
                        default=0.0, verbose_name="Height", db_column="hauteur"
                    ),
                ),
                (
                    "area",
                    models.FloatField(
                        default=0,
                        verbose_name="Area",
                        editable=False,
                        db_column="surface",
                    ),
                ),
                (
                    "material_cost",
                    models.FloatField(
                        default=0.0,
                        verbose_name="Material cost",
                        db_column="cout_materiel",
                    ),
                ),
                (
                    "heliport_cost",
                    models.FloatField(
                        default=0.0,
                        verbose_name="Heliport cost",
                        db_column="cout_heliport",
                    ),
                ),
                (
                    "subcontract_cost",
                    models.FloatField(
                        default=0.0,
                        verbose_name="Subcontract cost",
                        db_column="cout_soustraitant",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="Remarks and notes",
                        verbose_name="Description",
                        db_column="descriptif",
                        blank=True,
                    ),
                ),
            ],
            options={
                "db_table": "m_t_intervention",
                "verbose_name": "Intervention",
                "verbose_name_plural": "Interventions",
            },
            bases=(
                geotrek.common.mixins.models.AddPropertyMixin,
                mapentity.models.MapEntityMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="InterventionDisorder",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "disorder",
                    models.CharField(
                        max_length=128, verbose_name="Disorder", db_column="desordre"
                    ),
                ),
                (
                    "structure",
                    models.ForeignKey(
                        db_column="structure",
                        on_delete=django.db.models.deletion.CASCADE,
                        default=geotrek.authent.models.default_structure_pk,
                        verbose_name="Related structure",
                        to="authent.Structure",
                    ),
                ),
            ],
            options={
                "ordering": ["disorder"],
                "db_table": "m_b_desordre",
                "verbose_name": "Intervention's disorder",
                "verbose_name_plural": "Intervention's disorders",
            },
        ),
        migrations.CreateModel(
            name="InterventionJob",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "job",
                    models.CharField(
                        max_length=128, verbose_name="Job", db_column="fonction"
                    ),
                ),
                (
                    "cost",
                    models.DecimalField(
                        default=1.0,
                        decimal_places=2,
                        verbose_name="Cost",
                        max_digits=8,
                        db_column="cout_jour",
                    ),
                ),
                (
                    "structure",
                    models.ForeignKey(
                        db_column="structure",
                        on_delete=django.db.models.deletion.CASCADE,
                        default=geotrek.authent.models.default_structure_pk,
                        verbose_name="Related structure",
                        to="authent.Structure",
                    ),
                ),
            ],
            options={
                "ordering": ["job"],
                "db_table": "m_b_fonction",
                "verbose_name": "Intervention's job",
                "verbose_name_plural": "Intervention's jobs",
            },
        ),
        migrations.CreateModel(
            name="InterventionStatus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        max_length=128, verbose_name="Status", db_column="status"
                    ),
                ),
                (
                    "structure",
                    models.ForeignKey(
                        db_column="structure",
                        on_delete=django.db.models.deletion.CASCADE,
                        default=geotrek.authent.models.default_structure_pk,
                        verbose_name="Related structure",
                        to="authent.Structure",
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
                "db_table": "m_b_suivi",
                "verbose_name": "Intervention's status",
                "verbose_name_plural": "Intervention's statuses",
            },
        ),
        migrations.CreateModel(
            name="InterventionType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        max_length=128, verbose_name="Type", db_column="type"
                    ),
                ),
                (
                    "structure",
                    models.ForeignKey(
                        db_column="structure",
                        on_delete=django.db.models.deletion.CASCADE,
                        default=geotrek.authent.models.default_structure_pk,
                        verbose_name="Related structure",
                        to="authent.Structure",
                    ),
                ),
            ],
            options={
                "ordering": ["type"],
                "db_table": "m_b_intervention",
                "verbose_name": "Intervention's type",
                "verbose_name_plural": "Intervention's types",
            },
        ),
        migrations.CreateModel(
            name="ManDay",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "nb_days",
                    models.DecimalField(
                        decimal_places=2,
                        verbose_name="Mandays",
                        max_digits=6,
                        db_column="nb_jours",
                    ),
                ),
                (
                    "intervention",
                    models.ForeignKey(
                        to="maintenance.Intervention",
                        on_delete=django.db.models.deletion.CASCADE,
                        db_column="intervention",
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        db_column="fonction",
                        on_delete=django.db.models.deletion.CASCADE,
                        verbose_name="Job",
                        to="maintenance.InterventionJob",
                    ),
                ),
            ],
            options={
                "db_table": "m_r_intervention_fonction",
                "verbose_name": "Manday",
                "verbose_name_plural": "Mandays",
            },
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "date_insert",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Insertion date",
                        db_column="date_insert",
                    ),
                ),
                (
                    "date_update",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="Update date",
                        db_column="date_update",
                    ),
                ),
                (
                    "deleted",
                    models.BooleanField(
                        default=False,
                        verbose_name="Deleted",
                        editable=False,
                        db_column="supprime",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=128, verbose_name="Name", db_column="nom"
                    ),
                ),
                (
                    "begin_year",
                    models.IntegerField(
                        verbose_name="Begin year", db_column="annee_debut"
                    ),
                ),
                (
                    "end_year",
                    models.IntegerField(verbose_name="End year", db_column="annee_fin"),
                ),
                (
                    "constraint",
                    models.TextField(
                        help_text="Specific conditions, ...",
                        verbose_name="Constraint",
                        db_column="contraintes",
                        blank=True,
                    ),
                ),
                (
                    "global_cost",
                    models.FloatField(
                        default=0,
                        help_text="\u20ac",
                        verbose_name="Global cost",
                        db_column="cout_global",
                    ),
                ),
                (
                    "comments",
                    models.TextField(
                        help_text="Remarks and notes",
                        verbose_name="Comments",
                        db_column="commentaires",
                        blank=True,
                    ),
                ),
                (
                    "contractors",
                    models.ManyToManyField(
                        related_name="projects",
                        db_table="m_r_chantier_prestataire",
                        verbose_name="Contractors",
                        to="maintenance.Contractor",
                    ),
                ),
            ],
            options={
                "ordering": ["-begin_year", "name"],
                "db_table": "m_t_chantier",
                "verbose_name": "Project",
                "verbose_name_plural": "Projects",
            },
            bases=(
                geotrek.common.mixins.models.AddPropertyMixin,
                mapentity.models.MapEntityMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="ProjectDomain",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "domain",
                    models.CharField(
                        max_length=128, verbose_name="Domain", db_column="domaine"
                    ),
                ),
                (
                    "structure",
                    models.ForeignKey(
                        db_column="structure",
                        on_delete=django.db.models.deletion.CASCADE,
                        default=geotrek.authent.models.default_structure_pk,
                        verbose_name="Related structure",
                        to="authent.Structure",
                    ),
                ),
            ],
            options={
                "ordering": ["domain"],
                "db_table": "m_b_domaine",
                "verbose_name": "Project domain",
                "verbose_name_plural": "Project domains",
            },
        ),
        migrations.CreateModel(
            name="ProjectType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        max_length=128, verbose_name="Type", db_column="type"
                    ),
                ),
                (
                    "structure",
                    models.ForeignKey(
                        db_column="structure",
                        on_delete=django.db.models.deletion.CASCADE,
                        default=geotrek.authent.models.default_structure_pk,
                        verbose_name="Related structure",
                        to="authent.Structure",
                    ),
                ),
            ],
            options={
                "ordering": ["type"],
                "db_table": "m_b_chantier",
                "verbose_name": "Project type",
                "verbose_name_plural": "Project types",
            },
        ),
        migrations.AddField(
            model_name="project",
            name="domain",
            field=models.ForeignKey(
                db_column="domaine",
                on_delete=django.db.models.deletion.CASCADE,
                blank=True,
                to="maintenance.ProjectDomain",
                null=True,
                verbose_name="Domain",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="founders",
            field=models.ManyToManyField(
                to="common.Organism",
                verbose_name="Founders",
                through="maintenance.Funding",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="project_manager",
            field=models.ForeignKey(
                related_name="manage",
                on_delete=django.db.models.deletion.CASCADE,
                db_column="maitre_ouvrage",
                verbose_name="Project manager",
                to="common.Organism",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="project_owner",
            field=models.ForeignKey(
                related_name="own",
                on_delete=django.db.models.deletion.CASCADE,
                db_column="maitre_oeuvre",
                verbose_name="Project owner",
                to="common.Organism",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="structure",
            field=models.ForeignKey(
                db_column="structure",
                on_delete=django.db.models.deletion.CASCADE,
                default=geotrek.authent.models.default_structure_pk,
                verbose_name="Related structure",
                to="authent.Structure",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="type",
            field=models.ForeignKey(
                db_column="type",
                on_delete=django.db.models.deletion.CASCADE,
                blank=True,
                to="maintenance.ProjectType",
                null=True,
                verbose_name="Type",
            ),
        ),
        migrations.AddField(
            model_name="intervention",
            name="disorders",
            field=models.ManyToManyField(
                related_name="interventions",
                db_table="m_r_intervention_desordre",
                verbose_name="Disorders",
                to="maintenance.InterventionDisorder",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="intervention",
            name="jobs",
            field=models.ManyToManyField(
                to="maintenance.InterventionJob",
                verbose_name="Jobs",
                through="maintenance.ManDay",
            ),
        ),
        migrations.AddField(
            model_name="intervention",
            name="project",
            field=models.ForeignKey(
                related_name="interventions",
                on_delete=django.db.models.deletion.CASCADE,
                db_column="chantier",
                blank=True,
                to="maintenance.Project",
                null=True,
                verbose_name="Project",
            ),
        ),
        migrations.AddField(
            model_name="intervention",
            name="stake",
            field=models.ForeignKey(
                related_name="interventions",
                on_delete=django.db.models.deletion.CASCADE,
                db_column="enjeu",
                verbose_name="Stake",
                to="core.Stake",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="intervention",
            name="status",
            field=models.ForeignKey(
                db_column="status",
                on_delete=django.db.models.deletion.CASCADE,
                verbose_name="Status",
                to="maintenance.InterventionStatus",
            ),
        ),
        migrations.AddField(
            model_name="intervention",
            name="structure",
            field=models.ForeignKey(
                db_column="structure",
                on_delete=django.db.models.deletion.CASCADE,
                default=geotrek.authent.models.default_structure_pk,
                verbose_name="Related structure",
                to="authent.Structure",
            ),
        ),
        migrations.AddField(
            model_name="intervention",
            name="topology",
            field=models.ForeignKey(
                related_name="interventions_set",
                on_delete=django.db.models.deletion.CASCADE,
                verbose_name="Interventions",
                to="core.Topology",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="intervention",
            name="type",
            field=models.ForeignKey(
                db_column="type",
                on_delete=django.db.models.deletion.CASCADE,
                blank=True,
                to="maintenance.InterventionType",
                null=True,
                verbose_name="Type",
            ),
        ),
        migrations.AddField(
            model_name="funding",
            name="project",
            field=models.ForeignKey(
                db_column="chantier",
                on_delete=django.db.models.deletion.CASCADE,
                verbose_name="Project",
                to="maintenance.Project",
            ),
        ),
    ]
