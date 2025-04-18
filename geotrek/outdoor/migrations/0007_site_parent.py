# Generated by Django 3.1.4 on 2020-12-17 17:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("outdoor", "0006_auto_20201217_1545"),
    ]

    operations = [
        migrations.AddField(
            model_name="site",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="children",
                to="outdoor.site",
                verbose_name="Parent",
            ),
        ),
    ]
