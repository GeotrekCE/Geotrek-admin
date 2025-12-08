import django.contrib.gis.db.models.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        # ('core', '0001_initial'),
        # Commented in the goal of make the squash : 0100_initial work
    ]

    operations = [
        migrations.CreateModel(
            name="City",
            fields=[
                (
                    "code",
                    models.CharField(
                        max_length=6,
                        serialize=False,
                        primary_key=True,
                        db_column="insee",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=128, verbose_name="Name", db_column="commune"
                    ),
                ),
                (
                    "geom",
                    django.contrib.gis.db.models.fields.MultiPolygonField(
                        srid=settings.SRID, spatial_index=False
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "db_table": "l_commune",
                "verbose_name": "City",
                "verbose_name_plural": "Cities",
            },
        ),
        migrations.CreateModel(
            name="CityEdge",
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
                    "city",
                    models.ForeignKey(
                        db_column="commune",
                        on_delete=django.db.models.deletion.CASCADE,
                        verbose_name="City",
                        to="zoning.City",
                    ),
                ),
            ],
            options={
                "db_table": "f_t_commune",
                "verbose_name": "City edge",
                "verbose_name_plural": "City edges",
            },
            bases=("core.topology",),
        ),
        migrations.CreateModel(
            name="District",
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
                        max_length=128, verbose_name="Name", db_column="secteur"
                    ),
                ),
                (
                    "geom",
                    django.contrib.gis.db.models.fields.MultiPolygonField(
                        srid=settings.SRID, spatial_index=False
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "db_table": "l_secteur",
                "verbose_name": "District",
                "verbose_name_plural": "Districts",
            },
        ),
        migrations.CreateModel(
            name="DistrictEdge",
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
                    "district",
                    models.ForeignKey(
                        db_column="secteur",
                        on_delete=django.db.models.deletion.CASCADE,
                        verbose_name="District",
                        to="zoning.District",
                    ),
                ),
            ],
            options={
                "db_table": "f_t_secteur",
                "verbose_name": "District edge",
                "verbose_name_plural": "District edges",
            },
            bases=("core.topology",),
        ),
        migrations.CreateModel(
            name="RestrictedArea",
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
                        max_length=250, verbose_name="Name", db_column="zonage"
                    ),
                ),
                (
                    "geom",
                    django.contrib.gis.db.models.fields.MultiPolygonField(
                        srid=settings.SRID, spatial_index=False
                    ),
                ),
            ],
            options={
                "ordering": ["area_type", "name"],
                "db_table": "l_zonage_reglementaire",
                "verbose_name": "Restricted area",
                "verbose_name_plural": "Restricted areas",
            },
        ),
        migrations.CreateModel(
            name="RestrictedAreaEdge",
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
                    "restricted_area",
                    models.ForeignKey(
                        db_column="zone",
                        on_delete=django.db.models.deletion.CASCADE,
                        verbose_name="Restricted area",
                        to="zoning.RestrictedArea",
                    ),
                ),
            ],
            options={
                "db_table": "f_t_zonage",
                "verbose_name": "Restricted area edge",
                "verbose_name_plural": "Restricted area edges",
            },
            bases=("core.topology",),
        ),
        migrations.CreateModel(
            name="RestrictedAreaType",
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
                        max_length=200, verbose_name="Name", db_column="nom"
                    ),
                ),
            ],
            options={
                "db_table": "f_b_zonage",
                "verbose_name": "Restricted area type",
            },
        ),
        migrations.AddField(
            model_name="restrictedarea",
            name="area_type",
            field=models.ForeignKey(
                db_column="type",
                on_delete=django.db.models.deletion.CASCADE,
                verbose_name="Restricted area",
                to="zoning.RestrictedAreaType",
            ),
        ),
    ]
