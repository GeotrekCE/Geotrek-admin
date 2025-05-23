# Generated by Django 3.1.5 on 2021-02-18 07:34

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import geotrek.authent.models
import geotrek.common.mixins.models
import geotrek.zoning.mixins


class Migration(migrations.Migration):
    dependencies = [
        ("authent", "0005_remove_userprofile_language"),
        ("outdoor", "0016_auto_20210125_0726"),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
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
                        auto_now_add=True, verbose_name="Insertion date"
                    ),
                ),
                (
                    "date_update",
                    models.DateTimeField(
                        auto_now=True, db_index=True, verbose_name="Update date"
                    ),
                ),
                (
                    "published",
                    models.BooleanField(
                        default=False,
                        help_text="Visible on Geotrek-rando",
                        verbose_name="Published",
                    ),
                ),
                (
                    "publication_date",
                    models.DateField(
                        blank=True,
                        editable=False,
                        null=True,
                        verbose_name="Publication date",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Public name (Change carefully)",
                        max_length=128,
                        verbose_name="Name",
                    ),
                ),
                (
                    "review",
                    models.BooleanField(
                        default=False, verbose_name="Waiting for publication"
                    ),
                ),
                (
                    "geom",
                    django.contrib.gis.db.models.fields.GeometryCollectionField(
                        srid=settings.SRID, verbose_name="Location"
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Complete description",
                        verbose_name="Description",
                    ),
                ),
                (
                    "advice",
                    models.TextField(
                        blank=True,
                        help_text="Risks, danger, best period, ...",
                        verbose_name="Advice",
                    ),
                ),
                (
                    "eid",
                    models.CharField(
                        blank=True,
                        max_length=1024,
                        null=True,
                        verbose_name="External id",
                    ),
                ),
                (
                    "ratings",
                    models.ManyToManyField(
                        blank=True, related_name="courses", to="outdoor.Rating"
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="courses",
                        to="outdoor.site",
                        verbose_name="Site",
                    ),
                ),
                (
                    "structure",
                    models.ForeignKey(
                        default=geotrek.authent.models.default_structure_pk,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="authent.structure",
                        verbose_name="Related structure",
                    ),
                ),
            ],
            options={
                "verbose_name": "Outdoor course",
                "verbose_name_plural": "Outdoor courses",
                "ordering": ("name",),
            },
            bases=(
                geotrek.zoning.mixins.ZoningPropertiesMixin,
                geotrek.common.mixins.models.AddPropertyMixin,
                models.Model,
            ),
        ),
    ]
