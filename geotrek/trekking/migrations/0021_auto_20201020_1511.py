# Generated by Django 2.2.16 on 2020-10-20 15:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("trekking", "0020_remove_trek_is_park_centered"),
    ]

    operations = [
        migrations.AlterField(
            model_name="labeltrek",
            name="pictogram",
            field=models.FileField(
                blank=True,
                max_length=512,
                null=True,
                upload_to="upload",
                verbose_name="Pictogram",
            ),
        ),
    ]
