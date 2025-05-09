# Generated by Django 1.11.14 on 2019-08-09 09:47

import colorfield.fields
import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import geotrek.authent.models
import geotrek.common.mixins.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("common", "0004_attachment_creation_date"),
        ("authent", "0003_auto_20181203_1518"),
    ]

    operations = [
        migrations.CreateModel(
            name="Difficulty",
            fields=[
                (
                    "pictogram",
                    models.FileField(
                        blank=True,
                        db_column="picto",
                        max_length=512,
                        null=True,
                        upload_to="upload",
                        verbose_name="Pictogram",
                    ),
                ),
                (
                    "id",
                    models.IntegerField(
                        primary_key=True, serialize=False, verbose_name="Ordre"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_column="nom", max_length=128, verbose_name="Nom"
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
                "db_table": "g_b_difficulte",
                "verbose_name": "Niveau de difficult\xe9",
                "verbose_name_plural": "Niveaux de difficult\xe9",
            },
        ),
        migrations.CreateModel(
            name="Dive",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_insert",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_column="date_insert",
                        verbose_name="Insertion date",
                    ),
                ),
                (
                    "date_update",
                    models.DateTimeField(
                        auto_now=True,
                        db_column="date_update",
                        db_index=True,
                        verbose_name="Update date",
                    ),
                ),
                (
                    "deleted",
                    models.BooleanField(
                        db_column="supprime",
                        default=False,
                        editable=False,
                        verbose_name="Deleted",
                    ),
                ),
                (
                    "published",
                    models.BooleanField(
                        db_column="public",
                        default=False,
                        help_text="Online",
                        verbose_name="Published",
                    ),
                ),
                (
                    "publication_date",
                    models.DateField(
                        blank=True,
                        db_column="date_publication",
                        editable=False,
                        null=True,
                        verbose_name="Publication date",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_column="nom",
                        help_text="Public name (Change carefully)",
                        max_length=128,
                        verbose_name="Name",
                    ),
                ),
                (
                    "review",
                    models.BooleanField(
                        db_column="relecture",
                        default=False,
                        verbose_name="Waiting for publication",
                    ),
                ),
                (
                    "description_teaser",
                    models.TextField(
                        blank=True,
                        db_column="chapeau",
                        help_text="Bref r\xe9sum\xe9",
                        verbose_name="Chapeau",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        db_column="description",
                        help_text="Description compl\xe8te",
                        verbose_name="Description",
                    ),
                ),
                (
                    "owner",
                    models.CharField(
                        blank=True,
                        db_column="proprietaire",
                        max_length=256,
                        verbose_name="Propri\xe9taire",
                    ),
                ),
                (
                    "departure",
                    models.CharField(
                        blank=True,
                        db_column="depart",
                        max_length=128,
                        verbose_name="Departure area",
                    ),
                ),
                (
                    "disabled_sport",
                    models.TextField(
                        blank=True,
                        db_column="handicap",
                        verbose_name="Disabled sport accessibility",
                    ),
                ),
                (
                    "facilities",
                    models.TextField(
                        blank=True, db_column="equipements", verbose_name="Facilities"
                    ),
                ),
                (
                    "depth",
                    models.PositiveIntegerField(
                        blank=True,
                        db_column="profondeur",
                        help_text="m\xe8tres",
                        null=True,
                        verbose_name="Maximum depth",
                    ),
                ),
                (
                    "advice",
                    models.TextField(
                        blank=True,
                        db_column="recommandation",
                        help_text="Risques, danger, meilleure p\xe9riode, ...",
                        verbose_name="Recommandations",
                    ),
                ),
                (
                    "geom",
                    django.contrib.gis.db.models.fields.GeometryField(
                        srid=settings.SRID, verbose_name="Emplacement"
                    ),
                ),
                (
                    "eid",
                    models.CharField(
                        blank=True,
                        db_column="id_externe",
                        max_length=1024,
                        null=True,
                        verbose_name="ID externe",
                    ),
                ),
                (
                    "difficulty",
                    models.ForeignKey(
                        blank=True,
                        db_column="difficulte",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dives",
                        to="diving.Difficulty",
                        verbose_name="Niveau de difficult\xe9",
                    ),
                ),
            ],
            options={
                "db_table": "g_t_plongee",
                "verbose_name": "Dive",
                "verbose_name_plural": "Dives",
            },
            bases=(
                geotrek.common.mixins.models.AddPropertyMixin,
                geotrek.common.mixins.models.PicturesMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="Level",
            fields=[
                (
                    "pictogram",
                    models.FileField(
                        blank=True,
                        db_column="picto",
                        max_length=512,
                        null=True,
                        upload_to="upload",
                        verbose_name="Pictogram",
                    ),
                ),
                (
                    "id",
                    models.IntegerField(
                        primary_key=True, serialize=False, verbose_name="Ordre"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_column="nom", max_length=128, verbose_name="Nom"
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        db_column="description",
                        help_text="Description compl\xe8te",
                        verbose_name="Description",
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
                "db_table": "g_b_niveau",
                "verbose_name": "Technical level",
                "verbose_name_plural": "Technical levels",
            },
        ),
        migrations.CreateModel(
            name="Practice",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "pictogram",
                    models.FileField(
                        db_column="picto",
                        max_length=512,
                        null=True,
                        upload_to="upload",
                        verbose_name="Pictogram",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_column="nom", max_length=128, verbose_name="Nom"
                    ),
                ),
                (
                    "order",
                    models.IntegerField(
                        blank=True,
                        db_column="tri",
                        help_text="Ordre alphab\xe9tique si vide",
                        null=True,
                        verbose_name="Ordre",
                    ),
                ),
                (
                    "color",
                    colorfield.fields.ColorField(
                        db_column="couleur",
                        default="#444444",
                        help_text="Couleur d\xe9finie pour la pratique, utilis\xe9e seulement pour le mobile.",
                        max_length=18,
                        verbose_name="Couleur",
                    ),
                ),
            ],
            options={
                "ordering": ["order", "name"],
                "db_table": "g_b_pratique",
                "verbose_name": "Pratique",
                "verbose_name_plural": "Practices",
            },
        ),
        migrations.AddField(
            model_name="dive",
            name="levels",
            field=models.ManyToManyField(
                blank=True,
                db_table="g_r_plongee_niveau",
                related_name="dives",
                to="diving.Level",
                verbose_name="Technical levels",
            ),
        ),
        migrations.AddField(
            model_name="dive",
            name="portal",
            field=models.ManyToManyField(
                blank=True,
                db_table="g_r_plongee_portal",
                related_name="dives",
                to="common.TargetPortal",
                verbose_name="Portail",
            ),
        ),
        migrations.AddField(
            model_name="dive",
            name="practice",
            field=models.ForeignKey(
                blank=True,
                db_column="pratique",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="dives",
                to="diving.Practice",
                verbose_name="Pratique",
            ),
        ),
        migrations.AddField(
            model_name="dive",
            name="source",
            field=models.ManyToManyField(
                blank=True,
                db_table="g_r_plongee_source",
                related_name="dives",
                to="common.RecordSource",
                verbose_name="Source",
            ),
        ),
        migrations.AddField(
            model_name="dive",
            name="structure",
            field=models.ForeignKey(
                db_column="structure",
                default=geotrek.authent.models.default_structure_pk,
                on_delete=django.db.models.deletion.CASCADE,
                to="authent.Structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AddField(
            model_name="dive",
            name="themes",
            field=models.ManyToManyField(
                blank=True,
                db_table="g_r_plongee_theme",
                help_text="Th\xe8me(s) principal(aux)",
                related_name="dives",
                to="common.Theme",
                verbose_name="Th\xe8mes",
            ),
        ),
    ]
