# Generated by Django 3.1.14 on 2022-03-24 11:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("feedback", "0030_auto_20220324_0947"),
    ]

    operations = [
        migrations.AddField(
            model_name="report",
            name="eid",
            field=models.CharField(
                blank=True, default="", max_length=1024, verbose_name="External id"
            ),
        ),
    ]
