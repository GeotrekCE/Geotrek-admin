# Generated by Django 3.2.18 on 2023-04-07 13:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tourism", "0040_auto_20230407_0947"),
    ]

    operations = [
        migrations.AlterField(
            model_name="touristiceventparticipantcount",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="participants",
                to="tourism.touristiceventparticipantcategory",
                verbose_name="Category",
            ),
        ),
    ]
