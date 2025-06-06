# Generated by Django 3.2.18 on 2023-05-03 08:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authent", "0011_alter_userprofile_structure"),
        ("signage", "0028_auto_20230407_0947"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bladetype",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="sealing",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
        migrations.AlterField(
            model_name="signagetype",
            name="structure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="authent.structure",
                verbose_name="Related structure",
            ),
        ),
    ]
