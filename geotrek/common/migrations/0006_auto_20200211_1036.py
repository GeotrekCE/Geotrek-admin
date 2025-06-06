# Generated by Django 1.11.27 on 2020-02-11 10:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0005_auto_20191029_1110"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attachment",
            name="creation_date",
            field=models.DateField(blank=True, null=True, verbose_name="Creation Date"),
        ),
        migrations.AlterField(
            model_name="filetype",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="authent.Structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="organism",
            name="organism",
            field=models.CharField(max_length=128, verbose_name="Organism"),
        ),
        migrations.AlterField(
            model_name="organism",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="authent.Structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="recordsource",
            name="website",
            field=models.URLField(
                blank=True, max_length=256, null=True, verbose_name="Website"
            ),
        ),
        migrations.AlterField(
            model_name="targetportal",
            name="website",
            field=models.URLField(max_length=256, unique=True, verbose_name="Website"),
        ),
        migrations.AlterField(
            model_name="theme",
            name="label",
            field=models.CharField(max_length=128, verbose_name="Label"),
        ),
        migrations.AlterModelTable(
            name="attachment",
            table=None,
        ),
        migrations.AlterModelTable(
            name="filetype",
            table=None,
        ),
        migrations.AlterModelTable(
            name="organism",
            table=None,
        ),
        migrations.AlterModelTable(
            name="recordsource",
            table=None,
        ),
        migrations.AlterModelTable(
            name="targetportal",
            table=None,
        ),
        migrations.AlterModelTable(
            name="theme",
            table=None,
        ),
    ]
