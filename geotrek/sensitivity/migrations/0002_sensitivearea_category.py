from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sensitivity", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="sensitivearea",
            name="category",
            field=models.IntegerField(
                default=1,
                verbose_name="Regulatory area",
                db_column="categorie",
                choices=[(1, "Species"), (2, "Regulatory")],
            ),
            preserve_default=False,
        ),
    ]
