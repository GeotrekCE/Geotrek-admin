# Generated by Django 3.2.19 on 2023-08-04 13:47

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tourism", "0045_remove_old_organizer"),
    ]

    operations = [
        migrations.RenameField(
            model_name="touristicevent",
            old_name="organizer_temp",
            new_name="organizer",
        ),
    ]
