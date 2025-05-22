import django.contrib.gis.db.models.fields
from django.conf import settings
from django.db import migrations, models

import geotrek.authent.models
import geotrek.common.mixins.models


class Migration(migrations.Migration):
    dependencies = [
        ("authent", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SensitiveArea",
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
                    "published",
                    models.BooleanField(
                        default=False,
                        help_text="Online",
                        verbose_name="Published",
                        db_column="public",
                    ),
                ),
                (
                    "publication_date",
                    models.DateField(
                        verbose_name="Publication date",
                        null=True,
                        editable=False,
                        db_column="date_publication",
                        blank=True,
                    ),
                ),
                (
                    "geom",
                    django.contrib.gis.db.models.fields.PolygonField(
                        srid=settings.SRID
                    ),
                ),
            ],
            options={
                "db_table": "s_t_zone_sensible",
                "verbose_name": "Sensitive area",
                "verbose_name_plural": "Sensitive areas",
            },
            bases=(models.Model, geotrek.common.mixins.models.AddPropertyMixin),
        ),
        migrations.CreateModel(
            name="Species",
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
                    "pictogram",
                    models.FileField(
                        max_length=512,
                        null=True,
                        verbose_name="Pictogram",
                        db_column="picto",
                        upload_to="upload",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=250, verbose_name="Name", db_column="nom"
                    ),
                ),
                (
                    "period01",
                    models.BooleanField(
                        default=False, verbose_name="January", db_column="periode01"
                    ),
                ),
                (
                    "period02",
                    models.BooleanField(
                        default=False, verbose_name="February", db_column="periode02"
                    ),
                ),
                (
                    "period03",
                    models.BooleanField(
                        default=False, verbose_name="March", db_column="periode03"
                    ),
                ),
                (
                    "period04",
                    models.BooleanField(
                        default=False, verbose_name="April", db_column="periode04"
                    ),
                ),
                (
                    "period05",
                    models.BooleanField(
                        default=False, verbose_name="May", db_column="periode05"
                    ),
                ),
                (
                    "period06",
                    models.BooleanField(
                        default=False, verbose_name="June", db_column="periode06"
                    ),
                ),
                (
                    "period07",
                    models.BooleanField(
                        default=False, verbose_name="July", db_column="periode07"
                    ),
                ),
                (
                    "period08",
                    models.BooleanField(
                        default=False, verbose_name="August", db_column="periode08"
                    ),
                ),
                (
                    "period09",
                    models.BooleanField(
                        default=False, verbose_name="September", db_column="periode09"
                    ),
                ),
                (
                    "period10",
                    models.BooleanField(
                        default=False, verbose_name="October", db_column="periode10"
                    ),
                ),
                (
                    "period11",
                    models.BooleanField(
                        default=False, verbose_name="November", db_column="periode11"
                    ),
                ),
                (
                    "period12",
                    models.BooleanField(
                        default=False, verbose_name="Decembre", db_column="periode12"
                    ),
                ),
                ("url", models.URLField(verbose_name="URL", blank=True)),
            ],
            options={
                "ordering": ["name"],
                "db_table": "s_b_espece",
                "verbose_name": "Species",
                "verbose_name_plural": "Species",
            },
        ),
        migrations.CreateModel(
            name="SportPractice",
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
                    "name",
                    models.CharField(
                        max_length=250, verbose_name="Name", db_column="nom"
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "db_table": "s_b_pratique_sportive",
                "verbose_name": "Sport practice",
                "verbose_name_plural": "Sport practices",
            },
        ),
        migrations.AddField(
            model_name="species",
            name="practices",
            field=models.ManyToManyField(
                to="sensitivity.SportPractice",
                db_table="s_r_espece_pratique_sportive",
                verbose_name="Sport practices",
            ),
        ),
        migrations.AddField(
            model_name="sensitivearea",
            name="species",
            field=models.ForeignKey(
                db_column="espece",
                on_delete=django.db.models.deletion.CASCADE,
                verbose_name="Species",
                to="sensitivity.Species",
            ),
        ),
        migrations.AddField(
            model_name="sensitivearea",
            name="structure",
            field=models.ForeignKey(
                db_column="structure",
                on_delete=django.db.models.deletion.CASCADE,
                default=geotrek.authent.models.default_structure_pk,
                verbose_name="Related structure",
                to="authent.Structure",
            ),
        ),
    ]
