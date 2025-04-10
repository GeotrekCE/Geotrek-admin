# Generated by Django 3.2.18 on 2023-04-07 13:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("common", "0031_auto_20230407_0947"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accessibilityattachment",
            name="content_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AlterField(
            model_name="hdviewpoint",
            name="content_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="contenttypes.contenttype",
            ),
        ),
    ]
