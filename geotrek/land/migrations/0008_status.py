# Generated by Django 3.1.13 on 2021-11-29 09:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("land", "0007_auto_20200406_1410"),
    ]

    operations = [
        migrations.CreateModel(
            name="Status",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "Status",
                "verbose_name_plural": "Statuses",
            },
        ),
    ]
