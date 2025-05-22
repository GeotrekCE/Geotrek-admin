from django.db import migrations


def migrate_pictogram(apps, schema_editor):
    Line = apps.get_model("signage", "Line")
    LinePictogram = apps.get_model("signage", "LinePictogram")
    for line in Line.objects.exclude(pictogram_name=None):
        line_pictogram, created = LinePictogram.objects.get_or_create(
            label=line.pictogram_name
        )
        line.pictograms.add(line_pictogram)


def reverse_migrate_pictogram(apps, schema_editor):
    Line = apps.get_model("signage", "Line")
    for line in Line.objects.exclude(pictograms=None):
        line.pictogram_name = line.pictograms.first().label
        line.save()


class Migration(migrations.Migration):
    dependencies = [
        ("signage", "0033_auto_20230807_0831"),
    ]

    operations = [
        migrations.RunPython(migrate_pictogram, reverse_code=reverse_migrate_pictogram),
    ]
