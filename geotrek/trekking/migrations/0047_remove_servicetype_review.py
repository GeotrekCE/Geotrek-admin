# Generated by Django 3.2.20 on 2023-09-05 17:30

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("trekking", "0046_alter_weblink_category"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="servicetype",
            name="review",
        ),
    ]
