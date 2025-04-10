# Generated by Django 3.1.3 on 2020-11-17 13:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("maintenance", "0014_auto_20200316_1245"),
    ]

    operations = [
        migrations.AlterField(
            model_name="intervention",
            name="date_insert",
            field=models.DateTimeField(
                auto_now_add=True, verbose_name="Date d'insertion"
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="date_update",
            field=models.DateTimeField(
                auto_now=True, db_index=True, verbose_name="Date de modification"
            ),
        ),
        migrations.AlterField(
            model_name="intervention",
            name="deleted",
            field=models.BooleanField(
                default=False, editable=False, verbose_name="Supprimé"
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="date_insert",
            field=models.DateTimeField(
                auto_now_add=True, verbose_name="Date d'insertion"
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="date_update",
            field=models.DateTimeField(
                auto_now=True, db_index=True, verbose_name="Date de modification"
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="deleted",
            field=models.BooleanField(
                default=False, editable=False, verbose_name="Supprimé"
            ),
        ),
    ]
