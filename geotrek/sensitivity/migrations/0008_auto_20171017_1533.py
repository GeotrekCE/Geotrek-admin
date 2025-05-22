from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sensitivity", "0007_species_radius"),
    ]

    operations = [
        migrations.AlterField(
            model_name="species",
            name="radius",
            field=models.IntegerField(
                help_text="meters", null=True, verbose_name="Bubble radius", blank=True
            ),
        ),
    ]
