# Generated by Django 4.2.10 on 2024-03-04 15:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("feedback", "0040_alter_reportstatus_color"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pendingemail",
            name="recipient",
            field=models.EmailField(
                blank=True, max_length=256, null=True, verbose_name="Recipient"
            ),
        ),
    ]
