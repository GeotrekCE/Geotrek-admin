import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import geotrek.authent.models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Structure",
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
                ("name", models.CharField(max_length=256, verbose_name="Nom")),
            ],
            options={
                "ordering": ["name"],
                "verbose_name": "Structure",
                "verbose_name_plural": "Structures",
                "permissions": (("can_bypass_structure", "Can bypass structure"),),
            },
        ),
        migrations.CreateModel(
            name="UserProfile",
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
                    "language",
                    models.CharField(
                        default="fr",
                        max_length=10,
                        verbose_name="Language",
                        choices=[
                            ("en", "English"),
                            ("fr", "French"),
                            ("it", "Italian"),
                            ("es", "Spanish"),
                        ],
                    ),
                ),
                (
                    "structure",
                    models.ForeignKey(
                        db_column="structure",
                        default=geotrek.authent.models.default_structure_pk,
                        verbose_name="Related structure",
                        to="authent.Structure",
                        on_delete=django.db.models.deletion.CASCADE,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        to=settings.AUTH_USER_MODEL,
                        on_delete=django.db.models.deletion.CASCADE,
                    ),
                ),
            ],
            options={
                "verbose_name": "User's profile",
                "verbose_name_plural": "User's profiles",
            },
        ),
    ]
