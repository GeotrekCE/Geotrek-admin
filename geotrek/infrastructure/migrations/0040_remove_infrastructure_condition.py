# Generated by Django 3.2.25 on 2024-04-25 13:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("infrastructure", "0039_infrastructure_conditions"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="infrastructure",
            name="condition",
        ),
    ]
