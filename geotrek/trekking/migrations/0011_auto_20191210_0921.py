# Generated by Django 1.11.26 on 2019-12-10 09:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("trekking", "0010_auto_20191029_1443"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderedtrekchild",
            name="order",
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name="poi",
            name="description",
            field=models.TextField(
                blank=True,
                db_column="description",
                help_text="History, details,  ...",
                verbose_name="Description",
            ),
        ),
        migrations.AlterField(
            model_name="weblinkcategory",
            name="pictogram",
            field=models.FileField(
                db_column="picto",
                max_length=512,
                null=True,
                upload_to="upload",
                verbose_name="Pictogram",
            ),
        ),
    ]
