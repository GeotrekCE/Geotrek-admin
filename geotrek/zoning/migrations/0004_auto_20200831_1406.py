# Generated by Django 2.2.15 on 2020-08-31 14:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("zoning", "0003_auto_20200406_1412"),
    ]

    operations = [
        migrations.AddField(
            model_name="city",
            name="published",
            field=models.BooleanField(
                default=True,
                help_text="Visible on Geotrek-rando",
                verbose_name="Published",
            ),
        ),
        migrations.AddField(
            model_name="district",
            name="published",
            field=models.BooleanField(
                default=True,
                help_text="Visible on Geotrek-rando",
                verbose_name="Published",
            ),
        ),
        migrations.AddField(
            model_name="restrictedarea",
            name="published",
            field=models.BooleanField(
                default=True,
                help_text="Visible on Geotrek-rando",
                verbose_name="Published",
            ),
        ),
    ]
