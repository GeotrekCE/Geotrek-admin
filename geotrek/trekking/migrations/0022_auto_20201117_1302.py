# Generated by Django 3.1.3 on 2020-11-17 13:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("trekking", "0021_auto_20201020_1511"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accessibility",
            name="pictogram",
            field=models.FileField(
                blank=True,
                max_length=512,
                null=True,
                upload_to="upload",
                verbose_name="Pictogramme",
            ),
        ),
        migrations.AlterField(
            model_name="difficultylevel",
            name="pictogram",
            field=models.FileField(
                blank=True,
                max_length=512,
                null=True,
                upload_to="upload",
                verbose_name="Pictogramme",
            ),
        ),
        migrations.AlterField(
            model_name="labeltrek",
            name="pictogram",
            field=models.FileField(
                blank=True,
                max_length=512,
                null=True,
                upload_to="upload",
                verbose_name="Pictogramme",
            ),
        ),
        migrations.AlterField(
            model_name="poi",
            name="name",
            field=models.CharField(
                help_text="Nom public (changez prudemment)",
                max_length=128,
                verbose_name="Nom",
            ),
        ),
        migrations.AlterField(
            model_name="poi",
            name="publication_date",
            field=models.DateField(
                blank=True,
                editable=False,
                null=True,
                verbose_name="Date de publication",
            ),
        ),
        migrations.AlterField(
            model_name="poi",
            name="published",
            field=models.BooleanField(
                default=False,
                help_text="Visible sur Geotrek-rando",
                verbose_name="Publié",
            ),
        ),
        migrations.AlterField(
            model_name="poi",
            name="review",
            field=models.BooleanField(
                default=False, verbose_name="En attente de publication"
            ),
        ),
        migrations.AlterField(
            model_name="poitype",
            name="pictogram",
            field=models.FileField(
                max_length=512,
                null=True,
                upload_to="upload",
                verbose_name="Pictogramme",
            ),
        ),
        migrations.AlterField(
            model_name="practice",
            name="pictogram",
            field=models.FileField(
                max_length=512,
                null=True,
                upload_to="upload",
                verbose_name="Pictogramme",
            ),
        ),
        migrations.AlterField(
            model_name="route",
            name="pictogram",
            field=models.FileField(
                blank=True,
                max_length=512,
                null=True,
                upload_to="upload",
                verbose_name="Pictogramme",
            ),
        ),
        migrations.AlterField(
            model_name="servicetype",
            name="name",
            field=models.CharField(
                help_text="Nom public (changez prudemment)",
                max_length=128,
                verbose_name="Nom",
            ),
        ),
        migrations.AlterField(
            model_name="servicetype",
            name="pictogram",
            field=models.FileField(
                max_length=512,
                null=True,
                upload_to="upload",
                verbose_name="Pictogramme",
            ),
        ),
        migrations.AlterField(
            model_name="servicetype",
            name="publication_date",
            field=models.DateField(
                blank=True,
                editable=False,
                null=True,
                verbose_name="Date de publication",
            ),
        ),
        migrations.AlterField(
            model_name="servicetype",
            name="published",
            field=models.BooleanField(
                default=False,
                help_text="Visible sur Geotrek-rando",
                verbose_name="Publié",
            ),
        ),
        migrations.AlterField(
            model_name="servicetype",
            name="review",
            field=models.BooleanField(
                default=False, verbose_name="En attente de publication"
            ),
        ),
        migrations.AlterField(
            model_name="trek",
            name="name",
            field=models.CharField(
                help_text="Nom public (changez prudemment)",
                max_length=128,
                verbose_name="Nom",
            ),
        ),
        migrations.AlterField(
            model_name="trek",
            name="publication_date",
            field=models.DateField(
                blank=True,
                editable=False,
                null=True,
                verbose_name="Date de publication",
            ),
        ),
        migrations.AlterField(
            model_name="trek",
            name="published",
            field=models.BooleanField(
                default=False,
                help_text="Visible sur Geotrek-rando",
                verbose_name="Publié",
            ),
        ),
        migrations.AlterField(
            model_name="trek",
            name="review",
            field=models.BooleanField(
                default=False, verbose_name="En attente de publication"
            ),
        ),
        migrations.AlterField(
            model_name="treknetwork",
            name="pictogram",
            field=models.FileField(
                max_length=512,
                null=True,
                upload_to="upload",
                verbose_name="Pictogramme",
            ),
        ),
        migrations.AlterField(
            model_name="weblinkcategory",
            name="pictogram",
            field=models.FileField(
                max_length=512,
                null=True,
                upload_to="upload",
                verbose_name="Pictogramme",
            ),
        ),
    ]
