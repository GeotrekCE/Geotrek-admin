# Generated by Django 2.2.14 on 2020-07-08 14:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("signage", "0016_auto_20200512_0805"),
    ]

    operations = [
        migrations.AlterField(
            model_name="line",
            name="distance",
            field=models.DecimalField(
                blank=True,
                decimal_places=1,
                help_text="km",
                max_digits=8,
                null=True,
                verbose_name="Distance",
            ),
        ),
    ]
