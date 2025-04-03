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
    ]

    operations = [
        migrations.CreateModel(
            name="InformationDesk",
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
                        max_length=256, verbose_name="Title", db_column="nom"
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="Brief description",
                        verbose_name="Description",
                        db_column="description",
                        blank=True,
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        max_length=32,
                        null=True,
                        verbose_name="Phone",
                        db_column="telephone",
                        blank=True,
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=256,
                        null=True,
                        verbose_name="Email",
                        db_column="email",
                        blank=True,
                    ),
                ),
                (
                    "website",
                    models.URLField(
                        max_length=256,
                        null=True,
                        verbose_name="Website",
                        db_column="website",
                        blank=True,
                    ),
                ),
                (
                    "photo",
                    models.FileField(
                        db_column="photo",
                        upload_to="upload",
                        max_length=512,
                        blank=True,
                        null=True,
                        verbose_name="Photo",
                    ),
                ),
                (
                    "street",
                    models.CharField(
                        max_length=256,
                        null=True,
                        verbose_name="Street",
                        db_column="rue",
                        blank=True,
                    ),
                ),
                (
                    "postal_code",
                    models.CharField(
                        max_length=8,
                        null=True,
                        verbose_name="Postal code",
                        db_column="code",
                        blank=True,
                    ),
                ),
                (
                    "municipality",
                    models.CharField(
                        max_length=256,
                        null=True,
                        verbose_name="Municipality",
                        db_column="commune",
                        blank=True,
                    ),
                ),
                (
                    "geom",
                    django.contrib.gis.db.models.fields.PointField(
                        db_column="geom",
                        verbose_name="Emplacement",
                        blank=True,
                        srid=settings.SRID,
                        null=True,
                        spatial_index=False,
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "db_table": "t_b_renseignement",
                "verbose_name": "Information desk",
                "verbose_name_plural": "Information desks",
            },
        ),
        migrations.CreateModel(
            name="InformationDeskType",
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
                    "label",
                    models.CharField(
                        max_length=128, verbose_name="Label", db_column="label"
                    ),
                ),
            ],
            options={
                "ordering": ["label"],
                "db_table": "t_b_type_renseignement",
                "verbose_name": "Information desk type",
                "verbose_name_plural": "Information desk types",
            },
        ),
        migrations.CreateModel(
            name="ReservationSystem",
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
                    models.CharField(unique=True, max_length=256, verbose_name="Name"),
                ),
            ],
            options={
                "db_table": "t_b_systeme_reservation",
                "verbose_name": "Reservation system",
                "verbose_name_plural": "Reservation systems",
            },
        ),
        migrations.CreateModel(
            name="TouristicContent",
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
                    "name",
                    models.CharField(
                        help_text="Public name (Change carefully)",
                        max_length=128,
                        verbose_name="Name",
                        db_column="nom",
                    ),
                ),
                (
                    "review",
                    models.BooleanField(
                        default=False,
                        verbose_name="Waiting for publication",
                        db_column="relecture",
                    ),
                ),
                (
                    "description_teaser",
                    models.TextField(
                        help_text="A brief summary",
                        verbose_name="Description teaser",
                        db_column="chapeau",
                        blank=True,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="Complete description",
                        verbose_name="Description",
                        db_column="description",
                        blank=True,
                    ),
                ),
                (
                    "geom",
                    django.contrib.gis.db.models.fields.GeometryField(
                        srid=settings.SRID, verbose_name="Location"
                    ),
                ),
                (
                    "contact",
                    models.TextField(
                        help_text="Address, phone, etc.",
                        verbose_name="Contact",
                        db_column="contact",
                        blank=True,
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=256,
                        null=True,
                        verbose_name="Email",
                        db_column="email",
                        blank=True,
                    ),
                ),
                (
                    "website",
                    models.URLField(
                        max_length=256,
                        null=True,
                        verbose_name="Website",
                        db_column="website",
                        blank=True,
                    ),
                ),
                (
                    "practical_info",
                    models.TextField(
                        help_text="Anything worth to know",
                        verbose_name="Practical info",
                        db_column="infos_pratiques",
                        blank=True,
                    ),
                ),
                (
                    "eid",
                    models.CharField(
                        max_length=128,
                        null=True,
                        verbose_name="External id",
                        db_column="id_externe",
                        blank=True,
                    ),
                ),
                (
                    "reservation_id",
                    models.CharField(
                        max_length=128,
                        verbose_name="Reservation ID",
                        db_column="id_reservation",
                        blank=True,
                    ),
                ),
                (
                    "approved",
                    models.BooleanField(
                        default=False, verbose_name="Approved", db_column="labellise"
                    ),
                ),
            ],
            options={
                "db_table": "t_t_contenu_touristique",
                "verbose_name": "Touristic content",
                "verbose_name_plural": "Touristic contents",
            },
            bases=(
                geotrek.common.mixins.models.AddPropertyMixin,
                mapentity.models.MapEntityMixin,
                geotrek.common.mixins.models.PicturesMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="TouristicContentCategory",
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
                    "label",
                    models.CharField(
                        max_length=128, verbose_name="Label", db_column="nom"
                    ),
                ),
                (
                    "geometry_type",
                    models.CharField(
                        default="point",
                        max_length=16,
                        db_column="type_geometrie",
                        choices=[
                            ("point", "Point"),
                            ("line", "Line"),
                            ("polygon", "Polygon"),
                            ("any", "Any"),
                        ],
                    ),
                ),
                (
                    "type1_label",
                    models.CharField(
                        max_length=128,
                        verbose_name="First list label",
                        db_column="label_type1",
                        blank=True,
                    ),
                ),
                (
                    "type2_label",
                    models.CharField(
                        max_length=128,
                        verbose_name="Second list label",
                        db_column="label_type2",
                        blank=True,
                    ),
                ),
                (
                    "order",
                    models.IntegerField(
                        help_text="Alphabetical order if blank",
                        null=True,
                        verbose_name="Order",
                        db_column="tri",
                        blank=True,
                    ),
                ),
            ],
            options={
                "ordering": ["order", "label"],
                "db_table": "t_b_contenu_touristique_categorie",
                "verbose_name": "Touristic content category",
                "verbose_name_plural": "Touristic content categories",
            },
        ),
        migrations.CreateModel(
            name="TouristicContentType",
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
                        db_column="picto",
                        upload_to="upload",
                        max_length=512,
                        blank=True,
                        null=True,
                        verbose_name="Pictogram",
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        max_length=128, verbose_name="Label", db_column="nom"
                    ),
                ),
                (
                    "in_list",
                    models.IntegerField(
                        db_column="liste_choix", choices=[(1, "First"), (2, "Second")]
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        related_name="types",
                        on_delete=django.db.models.deletion.CASCADE,
                        db_column="categorie",
                        verbose_name="Category",
                        to="tourism.TouristicContentCategory",
                    ),
                ),
            ],
            options={
                "ordering": ["label"],
                "db_table": "t_b_contenu_touristique_type",
                "verbose_name": "Touristic content type",
                "verbose_name_plural": "Touristic content type",
            },
        ),
        migrations.CreateModel(
            name="TouristicEvent",
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
                    "name",
                    models.CharField(
                        help_text="Public name (Change carefully)",
                        max_length=128,
                        verbose_name="Name",
                        db_column="nom",
                    ),
                ),
                (
                    "review",
                    models.BooleanField(
                        default=False,
                        verbose_name="Waiting for publication",
                        db_column="relecture",
                    ),
                ),
                (
                    "description_teaser",
                    models.TextField(
                        help_text="A brief summary",
                        verbose_name="Description teaser",
                        db_column="chapeau",
                        blank=True,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="Complete description",
                        verbose_name="Description",
                        db_column="description",
                        blank=True,
                    ),
                ),
                (
                    "geom",
                    django.contrib.gis.db.models.fields.PointField(
                        srid=settings.SRID, verbose_name="Location"
                    ),
                ),
                (
                    "begin_date",
                    models.DateField(
                        null=True,
                        verbose_name="Begin date",
                        db_column="date_debut",
                        blank=True,
                    ),
                ),
                (
                    "end_date",
                    models.DateField(
                        null=True,
                        verbose_name="End date",
                        db_column="date_fin",
                        blank=True,
                    ),
                ),
                (
                    "duration",
                    models.CharField(
                        help_text="3 days, season, ...",
                        max_length=64,
                        verbose_name="Duration",
                        db_column="duree",
                        blank=True,
                    ),
                ),
                (
                    "meeting_point",
                    models.CharField(
                        help_text="Where exactly ?",
                        max_length=256,
                        verbose_name="Meeting point",
                        db_column="point_rdv",
                        blank=True,
                    ),
                ),
                (
                    "meeting_time",
                    models.TimeField(
                        help_text="11:00, 23:30",
                        null=True,
                        verbose_name="Meeting time",
                        db_column="heure_rdv",
                        blank=True,
                    ),
                ),
                (
                    "contact",
                    models.TextField(
                        verbose_name="Contact", db_column="contact", blank=True
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=256,
                        null=True,
                        verbose_name="Email",
                        db_column="email",
                        blank=True,
                    ),
                ),
                (
                    "website",
                    models.URLField(
                        max_length=256,
                        null=True,
                        verbose_name="Website",
                        db_column="website",
                        blank=True,
                    ),
                ),
                (
                    "organizer",
                    models.CharField(
                        max_length=256,
                        verbose_name="Organizer",
                        db_column="organisateur",
                        blank=True,
                    ),
                ),
                (
                    "speaker",
                    models.CharField(
                        max_length=256,
                        verbose_name="Speaker",
                        db_column="intervenant",
                        blank=True,
                    ),
                ),
                (
                    "accessibility",
                    models.CharField(
                        max_length=256,
                        verbose_name="Accessibility",
                        db_column="accessibilite",
                        blank=True,
                    ),
                ),
                (
                    "participant_number",
                    models.CharField(
                        max_length=256,
                        verbose_name="Number of participants",
                        db_column="nb_places",
                        blank=True,
                    ),
                ),
                (
                    "booking",
                    models.TextField(
                        verbose_name="Booking", db_column="reservation", blank=True
                    ),
                ),
                (
                    "target_audience",
                    models.CharField(
                        max_length=128,
                        null=True,
                        verbose_name="Target audience",
                        db_column="public_vise",
                        blank=True,
                    ),
                ),
                (
                    "practical_info",
                    models.TextField(
                        help_text="Recommandations / To plan / Advices",
                        verbose_name="Practical info",
                        db_column="infos_pratiques",
                        blank=True,
                    ),
                ),
                (
                    "eid",
                    models.CharField(
                        max_length=128,
                        null=True,
                        verbose_name="External id",
                        db_column="id_externe",
                        blank=True,
                    ),
                ),
                (
                    "approved",
                    models.BooleanField(
                        default=False, verbose_name="Approved", db_column="labellise"
                    ),
                ),
                (
                    "portal",
                    models.ManyToManyField(
                        related_name="touristicevents",
                        db_table="t_r_evenement_touristique_portal",
                        verbose_name="Portal",
                        to="common.TargetPortal",
                        blank=True,
                    ),
                ),
                (
                    "source",
                    models.ManyToManyField(
                        related_name="touristicevents",
                        db_table="t_r_evenement_touristique_source",
                        verbose_name="Source",
                        to="common.RecordSource",
                        blank=True,
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
                (
                    "themes",
                    models.ManyToManyField(
                        related_name="touristic_events",
                        to="common.Theme",
                        db_table="t_r_evenement_touristique_theme",
                        blank=True,
                        help_text="Main theme(s)",
                        verbose_name="Themes",
                    ),
                ),
            ],
            options={
                "ordering": ["-begin_date"],
                "db_table": "t_t_evenement_touristique",
                "verbose_name": "Touristic event",
                "verbose_name_plural": "Touristic events",
            },
            bases=(
                geotrek.common.mixins.models.AddPropertyMixin,
                mapentity.models.MapEntityMixin,
                geotrek.common.mixins.models.PicturesMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="TouristicEventType",
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
                        db_column="picto",
                        upload_to="upload",
                        max_length=512,
                        blank=True,
                        null=True,
                        verbose_name="Pictogram",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        max_length=128, verbose_name="Type", db_column="type"
                    ),
                ),
            ],
            options={
                "ordering": ["type"],
                "db_table": "t_b_evenement_touristique_type",
                "verbose_name": "Touristic event type",
                "verbose_name_plural": "Touristic event types",
            },
        ),
        migrations.AddField(
            model_name="touristicevent",
            name="type",
            field=models.ForeignKey(
                db_column="type",
                on_delete=django.db.models.deletion.CASCADE,
                blank=True,
                to="tourism.TouristicEventType",
                null=True,
                verbose_name="Type",
            ),
        ),
        migrations.AddField(
            model_name="touristiccontent",
            name="category",
            field=models.ForeignKey(
                related_name="contents",
                on_delete=django.db.models.deletion.CASCADE,
                db_column="categorie",
                verbose_name="Category",
                to="tourism.TouristicContentCategory",
            ),
        ),
        migrations.AddField(
            model_name="touristiccontent",
            name="portal",
            field=models.ManyToManyField(
                related_name="touristiccontents",
                db_table="t_r_contenu_touristique_portal",
                verbose_name="Portal",
                to="common.TargetPortal",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="touristiccontent",
            name="reservation_system",
            field=models.ForeignKey(
                verbose_name="Reservation system",
                on_delete=django.db.models.deletion.CASCADE,
                blank=True,
                to="tourism.ReservationSystem",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="touristiccontent",
            name="source",
            field=models.ManyToManyField(
                related_name="touristiccontents",
                db_table="t_r_contenu_touristique_source",
                verbose_name="Source",
                to="common.RecordSource",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="touristiccontent",
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
            model_name="touristiccontent",
            name="themes",
            field=models.ManyToManyField(
                related_name="touristiccontents",
                to="common.Theme",
                db_table="t_r_contenu_touristique_theme",
                blank=True,
                help_text="Main theme(s)",
                verbose_name="Themes",
            ),
        ),
        migrations.AddField(
            model_name="touristiccontent",
            name="type1",
            field=models.ManyToManyField(
                related_name="contents1",
                db_table="t_r_contenu_touristique_type1",
                verbose_name="Type 1",
                to="tourism.TouristicContentType",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="touristiccontent",
            name="type2",
            field=models.ManyToManyField(
                related_name="contents2",
                db_table="t_r_contenu_touristique_type2",
                verbose_name="Type 2",
                to="tourism.TouristicContentType",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="informationdesk",
            name="type",
            field=models.ForeignKey(
                related_name="desks",
                on_delete=django.db.models.deletion.CASCADE,
                db_column="type",
                verbose_name="Type",
                to="tourism.InformationDeskType",
            ),
        ),
        migrations.CreateModel(
            name="TouristicContentType1",
            fields=[],
            options={
                "verbose_name": "Type",
                "proxy": True,
                "verbose_name_plural": "First list types",
            },
            bases=("tourism.touristiccontenttype",),
        ),
        migrations.CreateModel(
            name="TouristicContentType2",
            fields=[],
            options={
                "verbose_name": "Type",
                "proxy": True,
                "verbose_name_plural": "Second list types",
            },
            bases=("tourism.touristiccontenttype",),
        ),
    ]
