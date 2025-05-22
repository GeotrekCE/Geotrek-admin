from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sensitivity", "0004_auto_20171005_1807"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sensitivearea",
            name="category",
        ),
        migrations.AddField(
            model_name="species",
            name="category",
            field=models.IntegerField(
                default=1,
                verbose_name="Category",
                db_column="categorie",
                choices=[(1, "Species"), (2, "Regulatory")],
            ),
        ),
    ]
