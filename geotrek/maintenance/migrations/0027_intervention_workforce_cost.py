# Generated by Django 3.2.23 on 2024-02-12 16:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("maintenance", "0026_rename_subcontract_cost_intervention_contractor_cost"),
    ]

    operations = [
        migrations.AddField(
            model_name="intervention",
            name="workforce_cost",
            field=models.FloatField(
                blank=True, default=0.0, null=True, verbose_name="Workforce cost"
            ),
        ),
    ]
