# Generated by Django 4.2.20 on 2025-03-26 08:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0037_annotationcategory_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="accessibilityattachment",
            name="creation_date",
        ),
        migrations.RemoveField(
            model_name="attachment",
            name="creation_date",
        ),
        migrations.AlterField(
            model_name="accessibilityattachment",
            name="date_update",
            field=models.DateTimeField(
                auto_now=True, db_index=True, verbose_name="Update date"
            ),
        ),
    ]
