# Generated by Django 3.1.13 on 2021-09-15 13:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("outdoor", "0025_merge_ratings_min_max"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="site",
            name="ratings_max",
        ),
        migrations.AddField(
            model_name="site",
            name="ratings",
            field=models.ManyToManyField(
                blank=True, related_name="sites", to="outdoor.Rating"
            ),
        ),
    ]
