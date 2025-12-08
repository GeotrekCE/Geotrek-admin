from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sensitivity", "0006_auto_20171016_1422"),
    ]

    operations = [
        migrations.AddField(
            model_name="species",
            name="radius",
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
