import django.db.models.deletion
import mapentity.models
from django.db import migrations, models

import geotrek.authent.models


class Migration(migrations.Migration):
    dependencies = [
        ("authent", "0001_initial"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BaseInfrastructure",
            fields=[
                (
                    "topo_object",
                    models.OneToOneField(
                        parent_link=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        db_column="evenement",
                        serialize=False,
                        to="core.Topology",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Reference, code, ...",
                        max_length=128,
                        verbose_name="Name",
                        db_column="nom",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="Specificites",
                        verbose_name="Description",
                        db_column="description",
                        blank=True,
                    ),
                ),
                (
                    "implantation_year",
                    models.PositiveSmallIntegerField(
                        null=True,
                        verbose_name="Implantation year",
                        db_column="annee_implantation",
                    ),
                ),
            ],
            options={
                "db_table": "a_t_amenagement",
            },
            bases=(mapentity.models.MapEntityMixin, "core.topology", models.Model),
        ),
        migrations.CreateModel(
            name="InfrastructureCondition",
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
                    "label",
                    models.CharField(
                        max_length=250, verbose_name="Name", db_column="etat"
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
                "db_table": "a_b_etat",
                "verbose_name": "Infrastructure Condition",
                "verbose_name_plural": "Infrastructure Conditions",
            },
        ),
        migrations.CreateModel(
            name="InfrastructureType",
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
                ("label", models.CharField(max_length=128, db_column="nom")),
                (
                    "type",
                    models.CharField(
                        max_length=1,
                        db_column="type",
                        choices=[
                            ("A", "Building"),
                            ("E", "Facility"),
                            ("S", "Signage"),
                        ],
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
                "ordering": ["label", "type"],
                "db_table": "a_b_amenagement",
                "verbose_name": "Infrastructure Type",
                "verbose_name_plural": "Infrastructure Types",
            },
        ),
        migrations.AddField(
            model_name="baseinfrastructure",
            name="condition",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                db_column="etat",
                blank=True,
                to="infrastructure.InfrastructureCondition",
                null=True,
                verbose_name="Condition",
            ),
        ),
        migrations.AddField(
            model_name="baseinfrastructure",
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
            model_name="baseinfrastructure",
            name="type",
            field=models.ForeignKey(
                db_column="type",
                on_delete=django.db.models.deletion.CASCADE,
                verbose_name="Type",
                to="infrastructure.InfrastructureType",
            ),
        ),
        migrations.CreateModel(
            name="Infrastructure",
            fields=[],
            options={
                "verbose_name": "Infrastructure",
                "proxy": True,
                "verbose_name_plural": "Infrastructures",
            },
            bases=("infrastructure.baseinfrastructure",),
        ),
        migrations.CreateModel(
            name="Signage",
            fields=[],
            options={
                "verbose_name": "Signage",
                "proxy": True,
                "verbose_name_plural": "Signages",
            },
            bases=("infrastructure.baseinfrastructure",),
        ),
    ]
