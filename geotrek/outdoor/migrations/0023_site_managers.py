# Generated by Django 3.1.8 on 2021-04-28 05:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0017_auto_20210121_0943"),
        ("outdoor", "0022_orderedcoursechild"),
    ]

    operations = [
        migrations.AddField(
            model_name="site",
            name="managers",
            field=models.ManyToManyField(
                blank=True, to="common.Organism", verbose_name="Managers"
            ),
        ),
    ]
