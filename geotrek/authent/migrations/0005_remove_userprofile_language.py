# Generated by Django 2.2.17 on 2020-11-18 11:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("authent", "0004_auto_20200211_1011"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="language",
        ),
    ]
