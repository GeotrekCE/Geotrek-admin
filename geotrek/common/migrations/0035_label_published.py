# Generated by Django 3.2.19 on 2023-07-13 14:40

from django.db import migrations, models


def set_labels_published(apps, schema):
    Label = apps.get_model("common", "Label")
    Label.objects.update(published=True)


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0034_alter_accessibilityattachment_creator"),
    ]

    operations = [
        migrations.AddField(
            model_name="label",
            name="published",
            field=models.BooleanField(
                default=False,
                help_text="Visible on Geotrek-rando",
                verbose_name="Published",
            ),
        ),
        migrations.RunPython(set_labels_published, migrations.RunPython.noop),
    ]
