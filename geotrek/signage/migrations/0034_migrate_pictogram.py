from django.db import migrations


def migrate_pictogram(apps, schema_editor):
    Line = apps.get_model('signage', 'Line')
    LinePictogram = apps.get_model('signage', 'LinePictogram')
    for line in Line.objects.all():
        if line.pictogram_name:
            line_pictogram, created = LinePictogram.objects.get_or_create(label=line.pictogram_name)
            line.pictograms.add(line_pictogram)


class Migration(migrations.Migration):

    dependencies = [
        ('signage', '0033_auto_20230807_0831'),
    ]

    operations = [
        migrations.RunPython(migrate_pictogram, reverse_code=migrations.RunPython.noop),
    ]
