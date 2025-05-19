from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sensitivity", "0011_auto_20171108_1608"),
    ]

    operations = [
        migrations.AlterField(
            model_name="species",
            name="radius",
            field=models.IntegerField(
                help_text="meters",
                null=True,
                verbose_name="Bubble radius",
                db_column="rayon",
                blank=True,
            ),
        ),
    ]
