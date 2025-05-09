# Generated by Django 4.2.20 on 2025-04-02 13:29

from django.db import migrations, models

import geotrek.common.functions


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0039_auto_20250402_1205"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="path",
            constraint=models.CheckConstraint(
                check=models.Q(("geom__isvalid", True)), name="core_path_geom_is_valid"
            ),
        ),
        migrations.AddConstraint(
            model_name="path",
            constraint=models.CheckConstraint(
                check=geotrek.common.functions.IsSimple("geom"),
                name="core_path_geom_is_simple",
            ),
        ),
    ]
