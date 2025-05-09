# Generated by Django 4.2.13 on 2024-07-30 09:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0036_accessmean"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnnotationCategory",
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
                    "pictogram",
                    models.FileField(
                        max_length=512,
                        null=True,
                        upload_to="upload",
                        verbose_name="Pictogram",
                    ),
                ),
                ("label", models.CharField(max_length=128, verbose_name="Name")),
            ],
            options={
                "verbose_name": "Annotation category",
                "verbose_name_plural": "Annotation categories",
                "ordering": ["label"],
            },
        ),
        migrations.AddField(
            model_name="hdviewpoint",
            name="annotations_categories",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
