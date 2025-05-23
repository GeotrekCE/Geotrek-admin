# Generated by Django 1.11.27 on 2020-02-11 15:23

import django.db.models.deletion
from django.db import migrations, models

import geotrek.authent.models


class Migration(migrations.Migration):
    dependencies = [
        ("sensitivity", "0015_auto_20180206_1238"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sensitivearea",
            name="date_update",
            field=models.DateTimeField(
                auto_now=True,
                db_column="date_update",
                db_index=True,
                verbose_name="Update date",
            ),
        ),
        migrations.AlterField(
            model_name="sensitivearea",
            name="deleted",
            field=models.BooleanField(
                default=False, editable=False, verbose_name="Deleted"
            ),
        ),
        migrations.AlterField(
            model_name="sensitivearea",
            name="eid",
            field=models.CharField(
                blank=True, max_length=1024, null=True, verbose_name="External id"
            ),
        ),
        migrations.AlterField(
            model_name="sensitivearea",
            name="publication_date",
            field=models.DateField(
                blank=True, editable=False, null=True, verbose_name="Publication date"
            ),
        ),
        migrations.AlterField(
            model_name="sensitivearea",
            name="published",
            field=models.BooleanField(
                default=False, help_text="Online", verbose_name="Published"
            ),
        ),
        migrations.AlterField(
            model_name="sensitivearea",
            name="species",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="sensitivity.Species",
                verbose_name="Sensitive area",
            ),
        ),
        migrations.AlterField(
            model_name="sensitivearea",
            name="structure",
            field=models.ForeignKey(
                default=geotrek.authent.models.default_structure_pk,
                on_delete=django.db.models.deletion.CASCADE,
                to="authent.Structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="species",
            name="category",
            field=models.IntegerField(
                choices=[(1, "Species"), (2, "Regulatory")],
                default=1,
                editable=False,
                verbose_name="Category",
            ),
        ),
        migrations.AlterField(
            model_name="species",
            name="eid",
            field=models.CharField(
                blank=True, max_length=1024, null=True, verbose_name="External id"
            ),
        ),
        migrations.AlterField(
            model_name="species",
            name="name",
            field=models.CharField(max_length=250, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="species",
            name="period01",
            field=models.BooleanField(default=False, verbose_name="January"),
        ),
        migrations.AlterField(
            model_name="species",
            name="period02",
            field=models.BooleanField(default=False, verbose_name="February"),
        ),
        migrations.AlterField(
            model_name="species",
            name="period03",
            field=models.BooleanField(default=False, verbose_name="March"),
        ),
        migrations.AlterField(
            model_name="species",
            name="period04",
            field=models.BooleanField(default=False, verbose_name="April"),
        ),
        migrations.AlterField(
            model_name="species",
            name="period05",
            field=models.BooleanField(default=False, verbose_name="May"),
        ),
        migrations.AlterField(
            model_name="species",
            name="period06",
            field=models.BooleanField(default=False, verbose_name="June"),
        ),
        migrations.AlterField(
            model_name="species",
            name="period07",
            field=models.BooleanField(default=False, verbose_name="July"),
        ),
        migrations.AlterField(
            model_name="species",
            name="period08",
            field=models.BooleanField(default=False, verbose_name="August"),
        ),
        migrations.AlterField(
            model_name="species",
            name="period09",
            field=models.BooleanField(default=False, verbose_name="September"),
        ),
        migrations.AlterField(
            model_name="species",
            name="period10",
            field=models.BooleanField(default=False, verbose_name="October"),
        ),
        migrations.AlterField(
            model_name="species",
            name="period11",
            field=models.BooleanField(default=False, verbose_name="November"),
        ),
        migrations.AlterField(
            model_name="species",
            name="period12",
            field=models.BooleanField(default=False, verbose_name="Decembre"),
        ),
        migrations.AlterField(
            model_name="species",
            name="practices",
            field=models.ManyToManyField(
                to="sensitivity.SportPractice", verbose_name="Sport practices"
            ),
        ),
        migrations.AlterField(
            model_name="species",
            name="radius",
            field=models.IntegerField(
                blank=True, help_text="meters", null=True, verbose_name="Bubble radius"
            ),
        ),
        migrations.AlterField(
            model_name="sportpractice",
            name="name",
            field=models.CharField(max_length=250, verbose_name="Name"),
        ),
        migrations.AlterModelTable(
            name="sensitivearea",
            table=None,
        ),
        migrations.AlterModelTable(
            name="species",
            table=None,
        ),
        migrations.AlterModelTable(
            name="sportpractice",
            table=None,
        ),
    ]
