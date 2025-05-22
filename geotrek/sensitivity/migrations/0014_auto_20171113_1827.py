from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sensitivity", "0013_auto_20171109_1836"),
    ]

    operations = [
        migrations.AddField(
            model_name="sensitivearea",
            name="eid",
            field=models.CharField(
                max_length=128,
                null=True,
                verbose_name="External id",
                db_column="id_externe",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="species",
            name="eid",
            field=models.CharField(
                max_length=128,
                null=True,
                verbose_name="External id",
                db_column="id_externe",
                blank=True,
            ),
        ),
    ]
