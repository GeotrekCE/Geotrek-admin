from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sensitivity", "0010_auto_20171031_1620"),
    ]

    operations = [
        migrations.AlterField(
            model_name="species",
            name="pictogram",
            field=models.FileField(
                db_column="picto",
                upload_to="upload",
                max_length=512,
                blank=True,
                null=True,
                verbose_name="Pictogram",
            ),
        ),
    ]
